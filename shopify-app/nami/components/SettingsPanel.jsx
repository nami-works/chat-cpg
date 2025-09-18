import React, { useState } from 'react';
import {
  Card,
  Text,
  TextField,
  Select,
  Button,
  FormLayout,
  Stack,
  Divider,
  Checkbox,
  RangeSlider,
  Banner
} from '@shopify/polaris';

export function SettingsPanel({ settings, onSettingsChange, blogs }) {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSettingChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const languageOptions = [
    { label: 'English', value: 'en' },
    { label: 'Spanish', value: 'es' },
    { label: 'French', value: 'fr' },
    { label: 'German', value: 'de' },
    { label: 'Portuguese', value: 'pt' }
  ];

  const toneOptions = [
    { label: 'Professional', value: 'professional' },
    { label: 'Casual', value: 'casual' },
    { label: 'Friendly', value: 'friendly' },
    { label: 'Authoritative', value: 'authoritative' },
    { label: 'Conversational', value: 'conversational' }
  ];

  const blogOptions = blogs.map(blog => ({
    label: blog.title,
    value: blog.handle
  }));

  return (
    <Stack vertical spacing="loose">
      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            Content Settings
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Configure your content generation preferences and publishing settings.
          </Text>
        </Card.Section>

        <Card.Section>
          <FormLayout>
            <Select
              label="Target Blog"
              options={blogOptions}
              value={localSettings.blogHandle}
              onChange={(value) => handleSettingChange('blogHandle', value)}
              helpText="Select which blog to publish content to"
            />

            <TextField
              label="Author Name"
              value={localSettings.author}
              onChange={(value) => handleSettingChange('author', value)}
              placeholder="Enter author name for blog posts"
              helpText="This will be used as the author for all generated blog posts"
            />

            <Select
              label="Content Language"
              options={languageOptions}
              value={localSettings.language}
              onChange={(value) => handleSettingChange('language', value)}
              helpText="Language for generated content"
            />

            <Select
              label="Content Tone"
              options={toneOptions}
              value={localSettings.tone}
              onChange={(value) => handleSettingChange('tone', value)}
              helpText="Tone and style for generated content"
            />
          </FormLayout>
        </Card.Section>
      </Card>

      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            SEO Settings
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Configure SEO optimization settings for your content.
          </Text>
        </Card.Section>

        <Card.Section>
          <FormLayout>
            <RangeSlider
              label="Target Word Count"
              value={localSettings.targetWordCount || 1000}
              onChange={(value) => handleSettingChange('targetWordCount', value)}
              min={300}
              max={3000}
              step={100}
              helpText="Target word count for blog posts"
            />

            <RangeSlider
              label="SEO Score Target"
              value={localSettings.seoScoreTarget || 80}
              onChange={(value) => handleSettingChange('seoScoreTarget', value)}
              min={60}
              max={100}
              step={5}
              helpText="Minimum SEO score for generated content"
            />

            <TextField
              label="Target Keywords"
              value={localSettings.targetKeywords || ''}
              onChange={(value) => handleSettingChange('targetKeywords', value)}
              placeholder="Enter comma-separated keywords"
              helpText="Primary keywords to optimize for"
            />

            <Checkbox
              label="Include product recommendations"
              checked={localSettings.includeProductRecommendations || false}
              onChange={(checked) => handleSettingChange('includeProductRecommendations', checked)}
              helpText="Include product recommendations in blog posts"
            />

            <Checkbox
              label="Generate internal links"
              checked={localSettings.generateInternalLinks || true}
              onChange={(checked) => handleSettingChange('generateInternalLinks', checked)}
              helpText="Automatically generate internal links to other blog posts"
            />
          </FormLayout>
        </Card.Section>
      </Card>

      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            Content Structure
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Configure the structure and format of your generated content.
          </Text>
        </Card.Section>

        <Card.Section>
          <FormLayout>
            <Checkbox
              label="Include table of contents"
              checked={localSettings.includeTableOfContents || true}
              onChange={(checked) => handleSettingChange('includeTableOfContents', checked)}
              helpText="Add a table of contents to longer blog posts"
            />

            <Checkbox
              label="Include call-to-action"
              checked={localSettings.includeCallToAction || true}
              onChange={(checked) => handleSettingChange('includeCallToAction', checked)}
              helpText="Add call-to-action buttons to blog posts"
            />

            <Checkbox
              label="Include social sharing buttons"
              checked={localSettings.includeSocialSharing || true}
              onChange={(checked) => handleSettingChange('includeSocialSharing', checked)}
              helpText="Add social sharing buttons to blog posts"
            />

            <TextField
              label="Custom Footer Text"
              value={localSettings.customFooterText || ''}
              onChange={(value) => handleSettingChange('customFooterText', value)}
              multiline={3}
              placeholder="Enter custom footer text for blog posts"
              helpText="Custom text to include at the end of each blog post"
            />
          </FormLayout>
        </Card.Section>
      </Card>

      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            Publishing Settings
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Configure how content is published to your store.
          </Text>
        </Card.Section>

        <Card.Section>
          <FormLayout>
            <Checkbox
              label="Auto-publish content"
              checked={localSettings.autoPublish || false}
              onChange={(checked) => handleSettingChange('autoPublish', checked)}
              helpText="Automatically publish generated content without review"
            />

            <Checkbox
              label="Send notifications"
              checked={localSettings.sendNotifications || true}
              onChange={(checked) => handleSettingChange('sendNotifications', checked)}
              helpText="Send notifications when content is published"
            />

            <TextField
              label="Publishing Schedule"
              value={localSettings.publishingSchedule || ''}
              onChange={(value) => handleSettingChange('publishingSchedule', value)}
              placeholder="e.g., Every Monday at 9 AM"
              helpText="Schedule for automatic content publishing"
            />
          </FormLayout>
        </Card.Section>
      </Card>

      {localSettings.autoPublish && (
        <Banner
          title="Auto-publish is enabled"
          status="warning"
        >
          <p>Content will be automatically published without review. Make sure your settings are correct before generating content.</p>
        </Banner>
      )}
    </Stack>
  );
}
