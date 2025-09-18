import React, { useState, useEffect } from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  Button,
  Spinner,
  Banner,
  Tabs,
  Frame,
  TopBar,
  Navigation,
  Modal,
  FormLayout,
  TextField,
  Select,
  Checkbox,
  ResourceList,
  ResourceItem,
  Thumbnail,
  Badge,
  ButtonGroup,
  Toast,
  Loading
} from '@shopify/polaris';
import { useAppBridge } from '@shopify/app-bridge-react';
import { useAuthenticatedFetch } from './hooks/useAuthenticatedFetch';
import { useShopifyAPI } from './hooks/useShopifyAPI';
import { useOpenAI } from './hooks/useOpenAI';
import { useContentGeneration } from './hooks/useContentGeneration';
import { ThemeRefinement } from './components/ThemeRefinement';
import { ProductSelector } from './components/ProductSelector';
import { ContentEditor } from './components/ContentEditor';
import { SettingsPanel } from './components/SettingsPanel';
import { translations } from './locales';

export default function App() {
  const app = useAppBridge();
  const fetch = useAuthenticatedFetch();
  const { products, blogs, shop, loading: shopifyLoading } = useShopifyAPI(fetch);
  const { generateThemes, generateContent, loading: aiLoading } = useOpenAI(fetch);
  const { processContent, uploadToShopify, loading: contentLoading } = useContentGeneration(fetch);
  
  const [activeTab, setActiveTab] = useState(0);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [themes, setThemes] = useState([]);
  const [generatedContent, setGeneratedContent] = useState([]);
  const [settings, setSettings] = useState({
    blogHandle: '',
    author: '',
    language: 'en',
    tone: 'professional'
  });
  const [toast, setToast] = useState({ show: false, content: '', error: false });

  const showToast = (content, error = false) => {
    setToast({ show: true, content, error });
  };

  const handleThemeGeneration = async (prompt) => {
    try {
      const generatedThemes = await generateThemes(prompt, selectedProducts);
      setThemes(generatedThemes);
      showToast('Themes generated successfully!');
    } catch (error) {
      showToast('Failed to generate themes', true);
    }
  };

  const handleContentGeneration = async () => {
    try {
      const content = await generateContent(themes, selectedProducts, settings);
      setGeneratedContent(content);
      showToast('Content generated successfully!');
    } catch (error) {
      showToast('Failed to generate content', true);
    }
  };

  const handlePublishContent = async () => {
    try {
      await uploadToShopify(generatedContent, settings);
      showToast('Content published to Shopify!');
    } catch (error) {
      showToast('Failed to publish content', true);
    }
  };

  const tabs = [
    {
      id: 'themes',
      content: 'Theme Generation',
      panel: (
        <ThemeRefinement
          onGenerateThemes={handleThemeGeneration}
          themes={themes}
          loading={aiLoading}
        />
      )
    },
    {
      id: 'products',
      content: 'Product Selection',
      panel: (
        <ProductSelector
          products={products}
          selectedProducts={selectedProducts}
          onSelectionChange={setSelectedProducts}
          loading={shopifyLoading}
        />
      )
    },
    {
      id: 'content',
      content: 'Content Editor',
      panel: (
        <ContentEditor
          themes={themes}
          generatedContent={generatedContent}
          onGenerateContent={handleContentGeneration}
          onPublishContent={handlePublishContent}
          loading={contentLoading}
        />
      )
    },
    {
      id: 'settings',
      content: 'Settings',
      panel: (
        <SettingsPanel
          settings={settings}
          onSettingsChange={setSettings}
          blogs={blogs}
        />
      )
    }
  ];

  if (shopifyLoading) {
    return (
      <Frame>
        <Page title="Nami SEO Lab">
          <Layout>
            <Layout.Section>
              <Card>
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                  <Spinner size="large" />
                  <Text variant="bodyMd" as="p" color="subdued">
                    Loading your store data...
                  </Text>
                </div>
              </Card>
            </Layout.Section>
          </Layout>
        </Page>
      </Frame>
    );
  }

  return (
    <Frame>
      <Page title="Nami SEO Lab" subtitle="AI-powered content generation for your store">
        <Layout>
          <Layout.Section>
            <Tabs
              tabs={tabs}
              selected={activeTab}
              onSelect={setActiveTab}
            >
              {tabs[activeTab].panel}
            </Tabs>
          </Layout.Section>
        </Layout>
        
        {toast.show && (
          <Toast
            content={toast.content}
            error={toast.error}
            onDismiss={() => setToast({ show: false, content: '', error: false })}
          />
        )}
      </Page>
    </Frame>
  );
}
