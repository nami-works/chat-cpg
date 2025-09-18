import React, { useState } from 'react';
import {
  Card,
  Text,
  Button,
  ButtonGroup,
  Stack,
  Badge,
  Modal,
  TextField,
  FormLayout,
  Select,
  Checkbox,
  List,
  Spinner,
  EmptyState,
  Tabs,
  Code
} from '@shopify/polaris';

export function ContentEditor({ 
  themes, 
  generatedContent, 
  onGenerateContent, 
  onPublishContent, 
  loading 
}) {
  const [selectedContent, setSelectedContent] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [contentToPublish, setContentToPublish] = useState([]);

  const handleGenerateContent = () => {
    if (themes.length === 0) {
      return;
    }
    onGenerateContent();
  };

  const handlePublishContent = () => {
    if (contentToPublish.length === 0) {
      return;
    }
    onPublishContent();
  };

  const handleContentSelection = (contentId) => {
    setSelectedContent(
      selectedContent === contentId ? null : contentId
    );
  };

  const handleEditContent = (content) => {
    setEditingContent(content);
    setShowEditModal(true);
  };

  const handleSaveEdit = () => {
    // This would save the edited content
    console.log('Saving edited content:', editingContent);
    setShowEditModal(false);
    setEditingContent(null);
  };

  const handleContentToggle = (contentId) => {
    setContentToPublish(prev => 
      prev.includes(contentId) 
        ? prev.filter(id => id !== contentId)
        : [...prev, contentId]
    );
  };

  const handleSelectAll = () => {
    if (contentToPublish.length === generatedContent.length) {
      setContentToPublish([]);
    } else {
      setContentToPublish(generatedContent.map(content => content.id));
    }
  };

  const renderContentItem = (content) => {
    const isSelected = selectedContent === content.id;
    const isMarkedForPublish = contentToPublish.includes(content.id);

    return (
      <Card key={content.id}>
        <Card.Section>
          <Stack distribution="equalSpacing" alignment="center">
            <Stack spacing="tight">
              <Text variant="bodyMd" fontWeight="bold" as="h3">
                {content.title}
              </Text>
              <Text variant="bodySm" as="p" color="subdued">
                {content.theme} • {content.wordCount} words
              </Text>
              <Stack spacing="extraTight">
                <Badge status="info">
                  {content.status}
                </Badge>
                {content.seoScore && (
                  <Badge status={content.seoScore > 80 ? 'success' : 'warning'}>
                    SEO: {content.seoScore}%
                  </Badge>
                )}
                {content.readabilityScore && (
                  <Badge status={content.readabilityScore > 70 ? 'success' : 'warning'}>
                    Readability: {content.readabilityScore}%
                  </Badge>
                )}
              </Stack>
            </Stack>
            <Stack spacing="tight">
              <Checkbox
                checked={isMarkedForPublish}
                onChange={() => handleContentToggle(content.id)}
              />
              <ButtonGroup>
                <Button
                  size="slim"
                  onClick={() => handleContentSelection(content.id)}
                >
                  {isSelected ? 'Hide' : 'Preview'}
                </Button>
                <Button
                  size="slim"
                  onClick={() => handleEditContent(content)}
                >
                  Edit
                </Button>
              </ButtonGroup>
            </Stack>
          </Stack>
        </Card.Section>

        {isSelected && (
          <Card.Section>
            <Tabs
              tabs={[
                { id: 'preview', content: 'Preview' },
                { id: 'html', content: 'HTML' },
                { id: 'seo', content: 'SEO Analysis' }
              ]}
            >
              <div style={{ padding: '1rem 0' }}>
                {selectedContent === content.id && (
                  <>
                    <div id="preview" style={{ display: 'block' }}>
                      <div dangerouslySetInnerHTML={{ __html: content.html }} />
                    </div>
                    <div id="html" style={{ display: 'none' }}>
                      <Code>{content.html}</Code>
                    </div>
                    <div id="seo" style={{ display: 'none' }}>
                      <Stack vertical spacing="loose">
                        <Text variant="bodyMd" as="h4">SEO Analysis</Text>
                        <List type="bullet">
                          <List.Item>Target Keywords: {content.targetKeywords.join(', ')}</List.Item>
                          <List.Item>Meta Description: {content.metaDescription}</List.Item>
                          <List.Item>Heading Structure: {content.headingStructure}</List.Item>
                          <List.Item>Internal Links: {content.internalLinks}</List.Item>
                        </List>
                      </Stack>
                    </div>
                  </>
                )}
              </div>
            </Tabs>
          </Card.Section>
        )}
      </Card>
    );
  };

  return (
    <Stack vertical spacing="loose">
      <Card>
        <Card.Section>
          <Stack distribution="equalSpacing" alignment="center">
            <Stack spacing="tight">
              <Text variant="headingMd" as="h2">
                Content Generation
              </Text>
              <Text variant="bodyMd" as="p" color="subdued">
                Generate and edit blog content based on your selected themes and products.
              </Text>
            </Stack>
            <ButtonGroup>
              <Button
                primary
                onClick={handleGenerateContent}
                loading={loading}
                disabled={themes.length === 0}
              >
                Generate Content
              </Button>
            </ButtonGroup>
          </Stack>
        </Card.Section>
      </Card>

      {generatedContent.length > 0 && (
        <Card>
          <Card.Section>
            <Stack distribution="equalSpacing" alignment="center">
              <Text variant="bodyMd" as="p">
                {contentToPublish.length} of {generatedContent.length} content pieces selected for publishing
              </Text>
              <ButtonGroup>
                <Button
                  onClick={handleSelectAll}
                  size="slim"
                >
                  {contentToPublish.length === generatedContent.length ? 'Deselect All' : 'Select All'}
                </Button>
                <Button
                  primary
                  onClick={handlePublishContent}
                  loading={loading}
                  disabled={contentToPublish.length === 0}
                >
                  Publish Selected
                </Button>
              </ButtonGroup>
            </Stack>
          </Card.Section>
        </Card>
      )}

      {generatedContent.length === 0 ? (
        <Card>
          <Card.Section>
            <EmptyState
              heading="No content generated yet"
              image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/emptystate-files.png"
            >
              <p>Generate content based on your themes and products to get started.</p>
            </EmptyState>
          </Card.Section>
        </Card>
      ) : (
        <Stack vertical spacing="loose">
          {generatedContent.map(renderContentItem)}
        </Stack>
      )}

      {loading && (
        <Card>
          <Card.Section>
            <Stack alignment="center">
              <Spinner size="small" />
              <Text variant="bodyMd" as="p" color="subdued">
                Generating content...
              </Text>
            </Stack>
          </Card.Section>
        </Card>
      )}

      {editingContent && (
        <Modal
          open={showEditModal}
          onClose={() => setShowEditModal(false)}
          title="Edit Content"
          primaryAction={{
            content: 'Save Changes',
            onAction: handleSaveEdit,
          }}
          secondaryActions={[
            {
              content: 'Cancel',
              onAction: () => setShowEditModal(false),
            },
          ]}
        >
          <Modal.Section>
            <FormLayout>
              <TextField
                label="Title"
                value={editingContent.title}
                onChange={(value) => setEditingContent({...editingContent, title: value})}
              />
              <TextField
                label="Content"
                value={editingContent.content}
                onChange={(value) => setEditingContent({...editingContent, content: value})}
                multiline={10}
              />
              <TextField
                label="Meta Description"
                value={editingContent.metaDescription}
                onChange={(value) => setEditingContent({...editingContent, metaDescription: value})}
              />
            </FormLayout>
          </Modal.Section>
        </Modal>
      )}
    </Stack>
  );
}
