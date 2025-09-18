import pandas as pd
import os
import json
import time
import random
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Diretório base para salvar o cache junto ao script
base_dir = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(base_dir, 'coordenadas_cache.json')

# Coordenadas conhecidas dos shoppings
shoppings_coords = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

@dataclass
class CustomerData:
    """Data class for customer information"""
    customer_id: str
    cep: str
    city: str
    state: str
    total_spent: float
    total_orders: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearest_shopping: Optional[str] = None
    distance_to_nearest: Optional[float] = None

@dataclass
class DensityAnalysis:
    """Data class for density analysis results"""
    cep: str
    customer_count: int
    total_revenue: float
    total_orders: int
    avg_order_value: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nearest_shopping: Optional[str] = None
    distance_to_nearest: Optional[float] = None

class EnhancedDistanciador:
    """Enhanced version of distanciador with Shopify data processing capabilities"""
    
    def __init__(self):
        self.cache = self.carregar_cache()
        self.geolocator = Nominatim(user_agent='enhanced_distanciador_kigen')
    
    def carregar_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load coordinate cache from file"""
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Erro ao carregar cache: {e}")
        return {}

    def salvar_cache(self):
        """Save coordinate cache to file"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")

    def obter_coordenadas(self, cep: str) -> Tuple[float, float]:
        """Get coordinates for a CEP with caching"""
        if cep in self.cache:
            return self.cache[cep]

        try:
            location = self.geolocator.geocode({'postalcode': cep, 'country': 'Brazil'}, timeout=10)
            coords = (location.latitude, location.longitude) if location else (None, None)
        except Exception as e:
            logger.warning(f"Erro ao geocodificar CEP {cep}: {e}")
            coords = (None, None)

        if coords != (None, None):
            self.cache[cep] = coords
            self.salvar_cache()
        
        # Rate limiting
        time.sleep(3 + random.random())
        return coords

    def calcular_distancia(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates"""
        if None in coords1 or None in coords2:
            return float('inf')
        return round(geodesic(coords1, coords2).km, 2)

    def processar_shopify_data(self, shopify_csv_path: str) -> pd.DataFrame:
        """Process Shopify customer export data"""
        logger.info("Processando dados do Shopify...")
        
        # Load Shopify data
        df = pd.read_csv(shopify_csv_path)
        
        # Clean and prepare data
        df['cep'] = df['Default Address Zip'].str.replace('-', '').str.strip()
        df['cep'] = df['cep'].astype(str).str.zfill(8)
        
        # Convert Total Spent to numeric, handling currency formatting
        df['Total Spent'] = pd.to_numeric(df['Total Spent'].str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0)
        df['Total Orders'] = pd.to_numeric(df['Total Orders'], errors='coerce').fillna(0)
        
        # Add coordinate columns
        df['latitude'] = None
        df['longitude'] = None
        
        # Process coordinates for unique CEPs
        unique_ceps = df['cep'].unique()
        logger.info(f"Processando {len(unique_ceps)} CEPs únicos...")
        
        for i, cep in enumerate(unique_ceps):
            if i % 10 == 0:
                logger.info(f"Progresso: {i}/{len(unique_ceps)} CEPs processados")
            
            coords = self.obter_coordenadas(cep)
            df.loc[df['cep'] == cep, ['latitude', 'longitude']] = [coords[0], coords[1]]
        
        # Calculate distances to shopping malls
        for shopping, coords_shop in shoppings_coords.items():
            df[f'distancia_{shopping}'] = df.apply(
                lambda row: self.calcular_distancia(
                    (row['latitude'], row['longitude']), 
                    coords_shop
                ) if row['latitude'] and row['longitude'] else float('inf'),
                axis=1
            )
        
        # Find nearest shopping mall
        shopping_columns = [f'distancia_{shopping}' for shopping in shoppings_coords.keys()]
        df['shopping_mais_proximo'] = df[shopping_columns].idxmin(axis=1).str.replace('distancia_', '')
        df['distancia_mais_proximo'] = df[shopping_columns].min(axis=1)
        
        logger.info("Processamento do Shopify concluído!")
        return df

    def analisar_densidade_consumidores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze consumer density by geographic areas"""
        logger.info("Analisando densidade de consumidores...")
        
        # Group by CEP to get density metrics
        density_analysis = df.groupby('cep').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'latitude': 'first',
            'longitude': 'first',
            'shopping_mais_proximo': 'first',
            'distancia_mais_proximo': 'first'
        }).reset_index()
        
        density_analysis.columns = [
            'cep', 'customer_count', 'total_revenue', 'total_orders',
            'latitude', 'longitude', 'nearest_shopping', 'distance_to_nearest'
        ]
        
        # Calculate average order value
        density_analysis['avg_order_value'] = (
            density_analysis['total_revenue'] / density_analysis['total_orders']
        ).fillna(0)
        
        # Add density categories
        density_analysis['density_category'] = pd.cut(
            density_analysis['customer_count'],
            bins=[0, 1, 5, 10, 20, float('inf')],
            labels=['Baixa', 'Média-Baixa', 'Média', 'Alta', 'Muito Alta']
        )
        
        logger.info(f"Densidade analisada para {len(density_analysis)} áreas geográficas")
        return density_analysis

    def analisar_densidade_por_cidade(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze consumer density by city"""
        logger.info("Analisando densidade por cidade...")
        
        city_density = df.groupby('Default Address City').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'cep': 'nunique'  # Number of unique CEPs
        }).reset_index()
        
        city_density.columns = ['cidade', 'total_customers', 'total_revenue', 'total_orders', 'unique_ceps']
        city_density['avg_order_value'] = city_density['total_revenue'] / city_density['total_orders']
        city_density['customers_per_cep'] = city_density['total_customers'] / city_density['unique_ceps']
        
        return city_density.sort_values('total_customers', ascending=False)

    def identificar_clusters_altos_valores(self, df: pd.DataFrame, 
                                        min_revenue: float = 1000,
                                        max_distance: float = 15) -> pd.DataFrame:
        """Identify high-value customer clusters near shopping malls"""
        logger.info("Identificando clusters de alto valor...")
        
        # Filter high-value customers within reasonable distance
        high_value = df[
            (df['Total Spent'] >= min_revenue) & 
            (df['distancia_mais_proximo'] <= max_distance)
        ].copy()
        
        # Group by shopping mall and analyze
        clusters = high_value.groupby('shopping_mais_proximo').agg({
            'Customer ID': 'count',
            'Total Spent': 'sum',
            'Total Orders': 'sum',
            'distancia_mais_proximo': 'mean'
        }).reset_index()
        
        clusters.columns = ['shopping', 'high_value_customers', 'total_revenue', 'total_orders', 'avg_distance']
        clusters['avg_customer_value'] = clusters['total_revenue'] / clusters['high_value_customers']
        
        return clusters.sort_values('total_revenue', ascending=False)

    def gerar_relatorio_completo(self, shopify_csv_path: str, output_dir: str = None) -> Dict:
        """Generate complete analysis report"""
        if output_dir is None:
            output_dir = base_dir
        
        logger.info("Gerando relatório completo...")
        
        # Process Shopify data
        df_shopify = self.processar_shopify_data(shopify_csv_path)
        
        # Analyze density
        df_density = self.analisar_densidade_consumidores(df_shopify)
        df_city_density = self.analisar_densidade_por_cidade(df_shopify)
        df_clusters = self.identificar_clusters_altos_valores(df_shopify)
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        df_shopify.to_csv(os.path.join(output_dir, f'shopify_processed_{timestamp}.csv'), index=False)
        df_density.to_csv(os.path.join(output_dir, f'consumer_density_{timestamp}.csv'), index=False)
        df_city_density.to_csv(os.path.join(output_dir, f'city_density_{timestamp}.csv'), index=False)
        df_clusters.to_csv(os.path.join(output_dir, f'high_value_clusters_{timestamp}.csv'), index=False)
        
        # Generate summary statistics
        summary = {
            'total_customers': len(df_shopify),
            'total_revenue': df_shopify['Total Spent'].sum(),
            'total_orders': df_shopify['Total Orders'].sum(),
            'unique_ceps': df_shopify['cep'].nunique(),
            'unique_cities': df_shopify['Default Address City'].nunique(),
            'avg_order_value': df_shopify['Total Spent'].sum() / df_shopify['Total Orders'].sum(),
            'top_cities': df_city_density.head(10).to_dict('records'),
            'shopping_distribution': df_shopify['shopping_mais_proximo'].value_counts().to_dict(),
            'high_value_clusters': df_clusters.to_dict('records')
        }
        
        # Save summary
        with open(os.path.join(output_dir, f'analysis_summary_{timestamp}.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info("Relatório completo gerado com sucesso!")
        return summary

    def processar_planilha_original(self, csv_path: str, max_iteracoes: int = 50):
        """Original distanciador functionality for CEP-only data"""
        logger.info("Processando planilha original...")
        
        for iteracao in range(max_iteracoes):
            df = pd.read_csv(csv_path, dtype=str)
            df['cep'] = df['cep'].astype(str).str.strip().str.zfill(8)

            for shopping in shoppings_coords:
                if shopping not in df.columns:
                    df[shopping] = ''

            if 'Shopping Mais Proximo' not in df.columns:
                df['Shopping Mais Proximo'] = ''

            if 'Estimado Por Proximidade' not in df.columns:
                df['Estimado Por Proximidade'] = ''

            colunas_dist = list(shoppings_coords.keys())
            colunas_todas = colunas_dist + ['Shopping Mais Proximo', 'Estimado Por Proximidade']
            pendentes = df[df[colunas_todas].isna().any(axis=1) | df[colunas_todas].eq('').any(axis=1)]

            if pendentes.empty:
                logger.info("✅ Nenhum CEP pendente restante.")
                break

            inicio_iteracao = time.time()
            for idx, row in pendentes.iterrows():
                cep = row['cep']
                coords = self.obter_coordenadas(cep)

                if None not in coords and df.at[idx, 'Estimado Por Proximidade'] == 'sim':
                    for col in colunas_todas:
                        df.at[idx, col] = ''
                    df.at[idx, 'Estimado Por Proximidade'] = ''
                
                if None in coords:
                    prefixo = cep[:7]
                    similares = df[
                        (df['cep'].str.startswith(prefixo)) &
                        (df[colunas_todas].notna().all(axis=1)) &
                        (df[colunas_todas].ne('').all(axis=1))
                    ]

                    if not similares.empty:
                        for shopping in shoppings_coords:
                            df.at[idx, shopping] = similares.iloc[0][shopping]
                        df.at[idx, 'Shopping Mais Proximo'] = similares.iloc[0]['Shopping Mais Proximo']
                        df.at[idx, 'Estimado Por Proximidade'] = 'sim'
                        continue

                distancias = {}
                for shopping, coords_shop in shoppings_coords.items():
                    distancia = self.calcular_distancia(coords, coords_shop)
                    df.at[idx, shopping] = distancia
                    distancias[shopping] = distancia
                shopping_proximo = min(distancias, key=distancias.get)
                df.at[idx, 'Shopping Mais Proximo'] = shopping_proximo

            df.to_csv(csv_path, index=False)

            pendentes_restantes = df[df[colunas_todas].isna().any(axis=1) | df[colunas_todas].eq('').any(axis=1)]
            duracao = time.time() - inicio_iteracao
            ceps_processados = len(pendentes) - len(pendentes_restantes)
            
            if ceps_processados > 0:
                tempo_medio = duracao / ceps_processados
                estimado_restante = tempo_medio * len(pendentes_restantes)
                minutos, segundos = divmod(int(estimado_restante), 60)
                logger.info(f'⏳ Estimativa de tempo restante: {minutos} min {segundos} s')
            else:
                logger.warning('⚠️ Nenhum CEP processado nesta rodada. Não é possível estimar o tempo.')

            logger.info(f"🔁 Iteracao {iteracao + 1} concluida. CEPs ainda pendentes apos esta rodada: {len(pendentes_restantes)}")

def main():
    """Main function to demonstrate usage"""
    distanciador = EnhancedDistanciador()
    
    # Example usage
    shopify_file = os.path.join(base_dir, 'customers_export.csv')
    
    if os.path.exists(shopify_file):
        logger.info("Processando dados do Shopify...")
        summary = distanciador.gerar_relatorio_completo(shopify_file)
        logger.info(f"Análise concluída! Total de clientes: {summary['total_customers']}")
    else:
        logger.info("Arquivo do Shopify não encontrado. Processando planilha original...")
        base_path = os.path.join(base_dir, 'base_ceps.csv')
        distanciador.processar_planilha_original(base_path)

if __name__ == "__main__":
    main() 