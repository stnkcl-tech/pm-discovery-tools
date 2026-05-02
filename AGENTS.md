# AI-PM-Skills Project

## Project Overview

This is a **knowledge and reference document repository** focused on Product Management frameworks, methodologies, and best practices. It does not contain source code, build systems, or runtime dependencies. The project is organized as a collection of PDF reference materials intended for study and consultation.

The materials center on modern product management philosophy—primarily the work of **Marty Cagan** (Silicon Valley Product Group) and related frameworks such as **Jobs-to-be-Done (JTBD)** and **User Journey Mapping**.

## Project Structure

```
.
├── _context/                          # Core reference materials
│   ├── INSPIRED-BY-MARTY-CAGAN-BOOK-SUMMARY-AND-PDF.pdf
│   ├── [Poster] Product Model First Principles.pdf
│   └── Product Model First Principles In Depth: Product Team and Product Strategy.pdf
│
└── Discovery/                         # Discovery-phase research materials
    └── _context/
        ├── Jobs-to-be-Done-Framework.pdf
        ├── Jobs-to-be-Done-Product-Framework-Guide.pdf
        └── User Journey Mapping.pdf
```

### Directory Conventions

- **`_context/`**: Each topical folder contains a `_context/` subdirectory that holds the actual reference documents. This naming convention appears consistently at both root and subdirectory levels.
- **`Discovery/`**: Contains materials specifically related to the product discovery phase—customer research, need identification, and problem-space exploration.

## Content Inventory

### `_context/` (Core Product Model)

| Document | Pages | Description |
|----------|-------|-------------|
| `INSPIRED-BY-MARTY-CAGAN-BOOK-SUMMARY-AND-PDF.pdf` | 8 | Book summary of *INSPIRED: How to Create Products Customers Love*. Covers key roles (PM, UX, Engineering), product discovery vs. execution, opportunity assessment, prototyping, and lessons from Apple. |
| `[Poster] Product Model First Principles.pdf` | 1 | One-page visual poster summarizing 20 product model first principles across Product Team, Product Strategy, Product Discovery, Product Delivery, and Product Culture. Based on Cagan's *TRANSFORMED*. |
| `Product Model First Principles In Depth: Product Team and Product Strategy.pdf` | 2 | Deep-dive article by Paweł Huryn analyzing the Product Team and Product Strategy principles from *TRANSFORMED*. |

### `Discovery/_context/` (Discovery Frameworks)

| Document | Pages | Description |
|----------|-------|-------------|
| `Jobs-to-be-Done-Framework.pdf` | 2 | Overview of Jobs-to-be-Done Theory by Tony Ulwick. Explains how JTBD provides a framework for defining, categorizing, and capturing customer needs to make innovation predictable. |
| `Jobs-to-be-Done-Product-Framework-Guide.pdf` | 13 | Comprehensive guide to applying the JTBD framework in product development. *(Note: text extraction was not possible for this document; content may be image-based or heavily formatted.)* |
| `User Journey Mapping.pdf` | 1 | Figma resource on user journey mapping. Covers key components, types of journey maps, and a five-step process for creating them. |

## Technology Stack

- **None**. This repository contains only PDF documents.
- No programming languages, frameworks, package managers, or build tools are used.
- No runtime environment is required.

## Build, Test, and Deployment

- **No build process**.
- **No tests**.
- **No deployment process**.

This repository is a static document collection. "Usage" consists of reading and referencing the PDFs.

## Development Conventions

Since this is a document repository rather than a code project, conventions are organizational:

1. **Folder-per-topic**: Each major topic or phase gets its own directory (e.g., `Discovery/`).
2. **`_context/` subdirectories**: Actual documents live inside `_context/` folders, not at the directory root. Maintain this pattern when adding new materials.
3. **Descriptive filenames**: Use clear, descriptive filenames that indicate the content and source/author where applicable.
4. **PDF format**: All documents are stored as PDFs for portability and consistency.

## Adding New Materials

When contributing new reference documents:

1. Choose the appropriate top-level folder (create one if a new topic area is introduced).
2. Place documents inside a `_context/` subdirectory within that folder.
3. Use descriptive filenames.
4. Prefer text-based or text-searchable PDFs when possible.
5. Update this `AGENTS.md` to document new additions.

## Security Considerations

- No secrets, credentials, or sensitive configuration files are present.
- All documents are publicly available reference materials.
- No network services or dependencies.
