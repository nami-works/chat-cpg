generate_alt_text

# Automated Alt Text Generation for Media Links

## 🎯 Problem

Automatically generate alternative descriptions (Alt Text) for a list of over **1,000 links** to media files (images and videos), focusing on **web accessibility** and **SEO**.

The descriptions must be **descriptive and objective**, allowing visually impaired users to understand the visual content and search engines to properly index the media.

## 🗂️ Input

- File: `Export_2025-05-21_120208.xlsx`
- Reference column: `link`
- Output format: **existing `Alt Text` column in the spreadsheet will be filled**

## 🧩 Functional Requirements

- Compare images contained in the links with a base of **already classified product images** to identify which products are present in the media.
- Perform **image content analysis** using **computer vision APIs** to identify elements, objects, scenarios and generate automatic descriptions.
- Support for both **local** and **cloud environment** processing.
- Possibility of subsequent **human validation** (optional).

## 🛠️ Proposed Flow for Kigen

1. **Initial Diagnosis**
   - Evaluate if generation can be solved with Python functions or requires multiagent CrewAI.
   - Consider integration of internal product databases and external APIs.

2. **Solution Research**
   - Explore tools and libraries such as:
     - `CLIP` (OpenAI)
     - `Google Vision API`
     - `Azure Computer Vision`
     - `Hugging Face transformers`
     - `Pillow` or `OpenCV` for preprocessing.

3. **Strategic Assessment**
   - Determine technical feasibility and integration cost of computer vision APIs.
   - Define whether the process will be local or cloud-based.

4. **Function Mapping**
   - Initial examples:
     - `download_media(link) -> local_file`
     - `compare_with_base(local_file, product_base) -> identified_products`
     - `analyze_content(local_file) -> content_description`
     - `generate_alt_text(identified_products, content_description) -> alt_text`
     - `update_spreadsheet(spreadsheet, link, alt_text)`

5. **Implementation and Testing**
   - Create modular functions.
   - Test with database subset.
   - Validate description accuracy.

## 📥 Expected Inputs in Kigen

{
  'problem': 'Automatically generate alternative descriptions (Alt Text) for a list of media links, comparing with internal product base and using computer vision APIs.',
  'base_data': 'Export_2025-05-21_120208.xlsx',
  'links_column': 'link',
  'language': 'to be defined',
  'est_volume': 'over 1,000 links',
  'context': ['Web accessibility', 'SEO']
}

## 📦 Expected Outputs

- Spreadsheet `Export_2025-05-21_120208.xlsx` with `Alt Text` column filled with automatically generated descriptions.

## ⚠️ Risks and Mitigations

| Risk                                           | Mitigation                                   |
|------------------------------------------------|---------------------------------------------|
| Need to use multiple AIs                        | Prioritization of OpenAI solutions, where API is already contracted |
| High cost with computer vision APIs             | Careful selection of images for intensive analysis |
| Invalid or inaccessible links                   | Prior checking function (`verify_link()`) |
| Conflict between detected product and content    | Optional manual validation in final stages |

## 🚀 Next Steps

1. Implement **mapping and comparison flow with product base**.
2. Integrate with **computer vision API**.
3. Process the complete database.
4. Define, later, the **default language**.

## 🚀 Next Steps