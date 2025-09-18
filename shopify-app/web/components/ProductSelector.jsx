import React, { useState, useMemo } from 'react';
import {
  Card,
  Text,
  TextField,
  Button,
  ResourceList,
  ResourceItem,
  Thumbnail,
  Badge,
  Stack,
  Checkbox,
  ButtonGroup,
  EmptyState,
  Spinner,
  Filters,
  ChoiceList,
  Pagination
} from '@shopify/polaris';

export function ProductSelector({ products, selectedProducts, onSelectionChange, loading }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortValue, setSortValue] = useState('title');
  const [filterValue, setFilterValue] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const filteredProducts = useMemo(() => {
    let filtered = products;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(product =>
        product.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Category filter
    if (filterValue !== 'all') {
      filtered = filtered.filter(product =>
        product.product_type === filterValue
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortValue) {
        case 'title':
          return a.title.localeCompare(b.title);
        case 'created_at':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'price':
          return parseFloat(a.variants[0]?.price || 0) - parseFloat(b.variants[0]?.price || 0);
        default:
          return 0;
      }
    });

    return filtered;
  }, [products, searchQuery, sortValue, filterValue]);

  const paginatedProducts = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredProducts.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredProducts, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);

  const handleProductSelection = (productId) => {
    const newSelection = selectedProducts.includes(productId)
      ? selectedProducts.filter(id => id !== productId)
      : [...selectedProducts, productId];
    onSelectionChange(newSelection);
  };

  const handleSelectAll = () => {
    if (selectedProducts.length === paginatedProducts.length) {
      onSelectionChange([]);
    } else {
      const allIds = paginatedProducts.map(product => product.id);
      onSelectionChange(allIds);
    }
  };

  const handleSelectAllFiltered = () => {
    const allFilteredIds = filteredProducts.map(product => product.id);
    onSelectionChange(allFilteredIds);
  };

  const getProductCategories = () => {
    const categories = [...new Set(products.map(product => product.product_type))];
    return categories.map(category => ({
      label: category || 'Uncategorized',
      value: category || 'uncategorized'
    }));
  };

  const sortOptions = [
    { label: 'Title A-Z', value: 'title' },
    { label: 'Newest First', value: 'created_at' },
    { label: 'Price Low-High', value: 'price' }
  ];

  const filterOptions = [
    { label: 'All Products', value: 'all' },
    ...getProductCategories()
  ];

  const renderProductItem = (product) => {
    const isSelected = selectedProducts.includes(product.id);
    const media = product.images[0]?.src || '/placeholder-product.png';
    const price = product.variants[0]?.price || '0.00';
    const status = product.status === 'active' ? 'success' : 'warning';

    return (
      <ResourceItem
        id={product.id}
        url={`#`}
        media={
          <Thumbnail
            source={media}
            alt={product.title}
            size="medium"
          />
        }
        accessibilityLabel={`View details for ${product.title}`}
      >
        <Stack distribution="equalSpacing" alignment="center">
          <Stack spacing="tight">
            <Text variant="bodyMd" fontWeight="bold" as="h3">
              {product.title}
            </Text>
            <Text variant="bodySm" as="p" color="subdued">
              {product.product_type || 'Uncategorized'}
            </Text>
            <Stack spacing="extraTight">
              <Badge status={status}>
                {product.status}
              </Badge>
              <Badge>
                ${price}
              </Badge>
              {product.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} status="info">
                  {tag}
                </Badge>
              ))}
            </Stack>
          </Stack>
          <Checkbox
            checked={isSelected}
            onChange={() => handleProductSelection(product.id)}
          />
        </Stack>
      </ResourceItem>
    );
  };

  if (loading) {
    return (
      <Card>
        <Card.Section>
          <Stack alignment="center">
            <Spinner size="large" />
            <Text variant="bodyMd" as="p" color="subdued">
              Loading products...
            </Text>
          </Stack>
        </Card.Section>
      </Card>
    );
  }

  return (
    <Stack vertical spacing="loose">
      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            Product Selection
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Select products to include in your content generation. These will be used to create product-focused blog posts.
          </Text>
        </Card.Section>

        <Card.Section>
          <Stack vertical spacing="loose">
            <Stack distribution="equalSpacing" alignment="center">
              <Text variant="bodyMd" as="p">
                {selectedProducts.length} of {products.length} products selected
              </Text>
              <ButtonGroup>
                <Button
                  onClick={handleSelectAll}
                  size="slim"
                >
                  Select Page
                </Button>
                <Button
                  onClick={handleSelectAllFiltered}
                  size="slim"
                >
                  Select All Filtered
                </Button>
              </ButtonGroup>
            </Stack>

            <Stack distribution="equalSpacing" alignment="center">
              <TextField
                label="Search products"
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search by title or tags..."
                clearButton
              />
              <Select
                label="Sort by"
                options={sortOptions}
                value={sortValue}
                onChange={setSortValue}
              />
              <Select
                label="Filter by category"
                options={filterOptions}
                value={filterValue}
                onChange={setFilterValue}
              />
            </Stack>
          </Stack>
        </Card.Section>
      </Card>

      <Card>
        <Card.Section>
          {paginatedProducts.length === 0 ? (
            <EmptyState
              heading="No products found"
              image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/emptystate-files.png"
            >
              <p>Try adjusting your search or filter criteria.</p>
            </EmptyState>
          ) : (
            <ResourceList
              resourceName={{ singular: 'product', plural: 'products' }}
              items={paginatedProducts}
              renderItem={renderProductItem}
            />
          )}
        </Card.Section>

        {totalPages > 1 && (
          <Card.Section>
            <Stack distribution="center">
              <Pagination
                hasPrevious={currentPage > 1}
                onPrevious={() => setCurrentPage(currentPage - 1)}
                hasNext={currentPage < totalPages}
                onNext={() => setCurrentPage(currentPage + 1)}
              />
            </Stack>
          </Card.Section>
        )}
      </Card>
    </Stack>
  );
}
