# Project Detail Page Design

## Goal

Add an independent public project detail page so interviewers can open one project and inspect its role, goals, technical choices, challenges, solutions, media, and links without relying on the chat assistant.

## Routes

The public frontend supports:

- `/projects/:id`
- `/dify/projects/:id`

The existing admin route detection stays unchanged. The public app continues to avoid a route library for this first detail page and uses a small pathname parser.

## Data

The page uses the existing `projectService.getProjectDetail(projectId)` method, which calls `/api/projects/{id}`. Backend changes are out of scope because the API already returns the `ProjectDetail` shape needed by the page.

## Layout

The detail page has:

- A compact top navigation with a return link to the portfolio home and a resume download action.
- A project header with project type, title, subtitle, summary, role, tech stack, and cover image.
- Detail sections for background, goals, features, challenges, solutions, and links. Empty sections are hidden.
- A media evidence section for project screenshots, videos, documents, or other published media. Empty media is hidden.
- Loading and error states with a clear return-home action.

The visual language follows the existing portfolio: restrained cards, 8px radius, dense information layout, existing color tokens, and mobile-first responsive behavior.

## Navigation

`ProjectGrid` links each card to the detail route using the numeric project id. Fallback projects also use their fallback ids, so local fallback cards still navigate to predictable paths.

## Testing

Frontend tests cover:

- Detail service requests `/dify/api/projects/{id}`.
- Path parsing recognizes `/projects/:id` and `/dify/projects/:id`.
- Invalid project paths do not trigger the detail page parser.

