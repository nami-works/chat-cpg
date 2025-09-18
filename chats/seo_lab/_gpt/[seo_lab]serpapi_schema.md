
openapi: 3.1.0
info:
  title: SerpApi Keywords API
  version: 2.1.0
  description: >
    Retrieve **organic keyword signals** from Google via SerpApi using the single `/search` endpoint. This spec
    explicitly allows only `google` (SERP: People Also Ask, Related Searches, Organic Results) and `google_autocomplete`
    (Autocomplete suggestions). The `google_ads` engine is **not** supported.
servers:
  - url: https://serpapi.com
    description: Production
paths:
  /search:
    get:
      operationId: getKeywords
      summary: Get organic keywords (PAA, Related, Autocomplete)
      description: >
        Keyword discovery via SerpApi. - `engine=google` → returns `people_also_ask`, `related_searches`, and
        `organic_results`. - `engine=google_autocomplete` → returns `suggestions`.
      parameters:
        - name: engine
          in: query
          required: true
          description: Choose organic keyword source (ads engines are not allowed).
          schema:
            type: string
            enum:
              - google
              - google_autocomplete
            default: google
        - name: api_key
          in: query
          required: true
          description: Your SerpApi API key.
          schema:
            type: string
        - name: q
          in: query
          required: true
          description: Query/seed term.
          schema:
            type: string
        - name: location
          in: query
          required: false
          description: Geographic location (e.g., "Austin,Texas,United States").
          schema:
            type: string
        - name: hl
          in: query
          required: false
          description: Interface language (e.g., "en").
          schema:
            type: string
        - name: gl
          in: query
          required: false
          description: Country code (e.g., "us").
          schema:
            type: string
        - name: google_domain
          in: query
          required: false
          description: Google domain (e.g., "google.com", "google.co.uk").
          schema:
            type: string
      responses:
        "200":
          description: Keyword data retrieved successfully
          content:
            application/json:
              schema:
                type: object
                description: >
                  SerpApi response with keyword-related sections. Depending on `engine`, the relevant arrays will be
                  present.
                properties:
                  people_also_ask:
                    type: array
                    description: Present when `engine=google`. PAA questions.
                    items:
                      type: object
                      additionalProperties: true
                  related_searches:
                    type: array
                    description: Present when `engine=google`. Related searches.
                    items:
                      type: object
                      additionalProperties: true
                  organic_results:
                    type: array
                    description: Present when `engine=google`. Organic SERP results.
                    items:
                      type: object
                      additionalProperties: true
                  suggestions:
                    type: array
                    description: Present when `engine=google_autocomplete`. Autocomplete suggestions.
                    items:
                      type: object
                      additionalProperties: true
                additionalProperties: true
        "400":
          description: Bad request (e.g., missing required parameters)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                additionalProperties: true
        "401":
          description: Unauthorized (invalid or missing api_key)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                additionalProperties: true
        "422":
          description: Invalid engine — only `google` or `google_autocomplete` are accepted
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: engine must be one of [google, google_autocomplete]
                additionalProperties: true
    post:
      operationId: postKeywords
      summary: Get organic keywords (PAA, Related, Autocomplete) via POST
      description: Same as GET but parameters are sent in the request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                engine:
                  type: string
                  description: Choose organic keyword source (ads engines are not allowed).
                  enum:
                    - google
                    - google_autocomplete
                  default: google
                api_key:
                  type: string
                  description: Your SerpApi API key.
                q:
                  type: string
                  description: Query/seed term.
                location:
                  type: string
                  description: Geographic location (e.g., "Austin,Texas,United States").
                hl:
                  type: string
                  description: Interface language (e.g., "en").
                gl:
                  type: string
                  description: Country code (e.g., "us").
                google_domain:
                  type: string
                  description: Google domain (e.g., "google.com", "google.co.uk").
              required:
                - engine
                - api_key
                - q
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                engine:
                  type: string
                  enum:
                    - google
                    - google_autocomplete
                  default: google
                api_key:
                  type: string
                q:
                  type: string
                location:
                  type: string
                hl:
                  type: string
                gl:
                  type: string
                google_domain:
                  type: string
              required:
                - engine
                - api_key
                - q
      responses:
        "200":
          description: Keyword data retrieved successfully
          content:
            application/json:
              schema:
                type: object
                description: Keyword-related sections (vary by engine).
                properties:
                  people_also_ask:
                    type: array
                    items:
                      type: object
                      additionalProperties: true
                  related_searches:
                    type: array
                    items:
                      type: object
                      additionalProperties: true
                  organic_results:
                    type: array
                    items:
                      type: object
                      additionalProperties: true
                  suggestions:
                    type: array
                    items:
                      type: object
                      additionalProperties: true
                additionalProperties: true
        "400":
          description: Bad request (e.g., missing required parameters)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                additionalProperties: true
        "401":
          description: Unauthorized (invalid or missing api_key)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                additionalProperties: true
        "422":
          description: Invalid engine — only `google` or `google_autocomplete` are accepted
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: engine must be one of [google, google_autocomplete]
                additionalProperties: true