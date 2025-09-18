import React, { useState } from 'react';
import {
  Card,
  Text,
  TextField,
  Button,
  ButtonGroup,
  List,
  Stack,
  Badge,
  Banner,
  Spinner,
  FormLayout,
  Select,
  Checkbox
} from '@shopify/polaris';

export function ThemeRefinement({ onGenerateThemes, themes, loading }) {
  const [prompt, setPrompt] = useState('');
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [selectedThemes, setSelectedThemes] = useState([]);
  const [showRefinement, setShowRefinement] = useState(false);

  const handleGenerateThemes = () => {
    if (prompt.trim()) {
      onGenerateThemes(prompt);
    }
  };

  const handleRefineThemes = () => {
    if (refinementPrompt.trim()) {
      // This would call the refinement API
      console.log('Refining themes with:', refinementPrompt);
    }
  };

  const handleThemeSelection = (themeId) => {
    setSelectedThemes(prev => 
      prev.includes(themeId) 
        ? prev.filter(id => id !== themeId)
        : [...prev, themeId]
    );
  };

  const handleSelectAll = () => {
    if (selectedThemes.length === themes.length) {
      setSelectedThemes([]);
    } else {
      setSelectedThemes(themes.map(theme => theme.id));
    }
  };

  return (
    <Stack vertical spacing="loose">
      <Card>
        <Card.Section>
          <Text variant="headingMd" as="h2">
            Theme Generation
          </Text>
          <Text variant="bodyMd" as="p" color="subdued">
            Describe your content goals and target audience to generate relevant themes.
          </Text>
        </Card.Section>
        
        <Card.Section>
          <FormLayout>
            <TextField
              label="Content Brief"
              value={prompt}
              onChange={setPrompt}
              multiline={4}
              placeholder="e.g., Create educational content about hair care for curly hair, focusing on natural ingredients and styling tips..."
              helpText="Be specific about your target audience, content goals, and key topics."
            />
            
            <ButtonGroup>
              <Button
                primary
                onClick={handleGenerateThemes}
                loading={loading}
                disabled={!prompt.trim()}
              >
                Generate Themes
              </Button>
            </ButtonGroup>
          </FormLayout>
        </Card.Section>
      </Card>

      {themes.length > 0 && (
        <Card>
          <Card.Section>
            <Stack distribution="equalSpacing" alignment="center">
              <Text variant="headingMd" as="h3">
                Generated Themes ({themes.length})
              </Text>
              <ButtonGroup>
                <Button
                  onClick={handleSelectAll}
                  size="slim"
                >
                  {selectedThemes.length === themes.length ? 'Deselect All' : 'Select All'}
                </Button>
                <Button
                  onClick={() => setShowRefinement(!showRefinement)}
                  size="slim"
                >
                  {showRefinement ? 'Hide' : 'Refine'} Themes
                </Button>
              </ButtonGroup>
            </Stack>
          </Card.Section>

          {showRefinement && (
            <Card.Section>
              <FormLayout>
                <TextField
                  label="Refinement Instructions"
                  value={refinementPrompt}
                  onChange={setRefinementPrompt}
                  multiline={2}
                  placeholder="e.g., Make themes more specific to our premium positioning, focus on seasonal trends..."
                />
                <Button
                  onClick={handleRefineThemes}
                  loading={loading}
                  disabled={!refinementPrompt.trim()}
                >
                  Refine Themes
                </Button>
              </FormLayout>
            </Card.Section>
          )}

          <Card.Section>
            <List type="bullet">
              {themes.map((theme) => (
                <List.Item key={theme.id}>
                  <Stack distribution="equalSpacing" alignment="center">
                    <Stack spacing="tight">
                      <Text variant="bodyMd" as="p">
                        {theme.title}
                      </Text>
                      <Text variant="bodySm" as="p" color="subdued">
                        {theme.description}
                      </Text>
                      <Stack spacing="extraTight">
                        {theme.keywords.map((keyword, index) => (
                          <Badge key={index} status="info">
                            {keyword}
                          </Badge>
                        ))}
                      </Stack>
                    </Stack>
                    <Checkbox
                      checked={selectedThemes.includes(theme.id)}
                      onChange={() => handleThemeSelection(theme.id)}
                    />
                  </Stack>
                </List.Item>
              ))}
            </List>
          </Card.Section>
        </Card>
      )}

      {loading && (
        <Card>
          <Card.Section>
            <Stack alignment="center">
              <Spinner size="small" />
              <Text variant="bodyMd" as="p" color="subdued">
                Generating themes...
              </Text>
            </Stack>
          </Card.Section>
        </Card>
      )}
    </Stack>
  );
}
