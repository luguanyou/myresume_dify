# Project Detail Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent public project detail page reachable from project cards.

**Architecture:** Keep the current no-router approach by extracting public route parsing into a small helper. Add a focused `ProjectDetailPage` component that loads `ProjectDetail` through the existing service and renders only non-empty sections.

**Tech Stack:** React, TypeScript, Vite, Vitest, existing CSS token system.

---

### Task 1: Route Parsing and Service Coverage

**Files:**
- Create: `frontend/src/routes.ts`
- Modify: `frontend/src/services/api.test.ts`
- Test: `frontend/src/services/api.test.ts`

- [ ] Add tests for `projectService.getProjectDetail(42)` and `getProjectRoute`.
- [ ] Run `npm test -- src/services/api.test.ts` and confirm the new tests fail because the route helper is missing.
- [ ] Implement `frontend/src/routes.ts` with a `getProjectRoute(pathname: string): { projectId: number } | null` helper.
- [ ] Run `npm test -- src/services/api.test.ts` and confirm the tests pass.

### Task 2: Public App Route Branch

**Files:**
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/components/public/ProjectDetailPage.tsx`

- [ ] Add an `App.tsx` branch that renders `ProjectDetailPage` when `getProjectRoute(window.location.pathname)` returns a project id.
- [ ] Implement `ProjectDetailPage` loading, success, empty-section hiding, error state, and media rendering.
- [ ] Keep resume download URLs using the existing `resumeDownloadUrl` constant.

### Task 3: Project Card Links

**Files:**
- Modify: `frontend/src/components/public/ProjectGrid.tsx`

- [ ] Replace the current `#assistant` detail link with `/projects/{project.id}`.
- [ ] Preserve the existing card layout and copy.

### Task 4: Detail Page Styling

**Files:**
- Modify: `frontend/src/App.css`

- [ ] Add CSS for detail navigation, header, meta panels, detail sections, links, media evidence, loading, and error states.
- [ ] Add mobile rules under the existing media queries so the detail grid collapses cleanly.

### Task 5: Verification

**Files:**
- Read: `frontend/src/App.tsx`
- Read: `frontend/src/components/public/ProjectDetailPage.tsx`
- Read: `frontend/src/components/public/ProjectGrid.tsx`
- Read: `frontend/src/App.css`

- [ ] Run `npm test`.
- [ ] Run `npm run lint`.
- [ ] Run `npm run build`.
- [ ] Review `git diff -- frontend/src/App.tsx frontend/src/routes.ts frontend/src/components/public/ProjectDetailPage.tsx frontend/src/components/public/ProjectGrid.tsx frontend/src/App.css frontend/src/services/api.test.ts`.

