---
name: evol-ai-frontend-design
description: Create distinctive, production-grade frontend interfaces for the ERP Evol AI Assistant. Use this skill when building web components, chat interfaces, or dashboard layouts for the ERP. Generates polished, strictly typed TypeScript code with a refined, professional, and highly usable aesthetic.
---

This skill guides the creation of the frontend interface for the **AI Assistant of ERP Evol**. Implement real working code with exceptional attention to aesthetic details, usability, and corporate professionalism, avoiding generic "AI slop" aesthetics.

## Design Thinking

Before coding, understand the context and commit to the project's aesthetic direction:
- **Purpose**: An AI support assistant integrated into an ERP system. It must be clear, trustworthy, highly legible, and efficient for business users.
- **Tone**: Choose a professional extreme: *Refined Minimalist*, *Industrial/Utilitarian*, or *Modern Corporate*. The design must be clean and data-focused. Avoid chaotic, overly playful, or maximalist elements.
- **Constraints (CRITICAL)**:
  - STRICT TypeScript with proper typing for API models (e.g., `ChatMessage`, `ChatRequest`, `ChatResponse`, `SourceReference`).
  - The UI and all visible text MUST be exclusively in Portuguese (pt-BR). Do not use i18n libraries.
  - NO file or image upload features.
  - NO WebSockets or push notifications (communication is strictly simple request/response).
- **Differentiation**: Make this enterprise chat interface feel premium, responsive, and deeply integrated. Focus on readability and fluid presentation of AI responses and source references.

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose clean, highly readable, and professional sans-serif fonts. The typography must support long chat reading without eye strain. Differentiate AI text, user text, and technical/code snippets clearly.
- **Color & Theme**: Commit to a cohesive corporate aesthetic. Use CSS variables for consistency. Prefer a refined palette with clear contrast for chat bubbles, user inputs, and system messages. Use sharp, intentional accents to highlight important actions, source links, or errors.
- **Motion**: Use subtle, performant animations for message appearances and loading states (e.g., skeleton loaders or typing indicators). Focus on micro-interactions that provide clear feedback without slowing down the user's workflow.
- **Spatial Composition**: Maintain a clear visual hierarchy. Use generous negative space to separate chat messages and contextual references. Ensure the chat input area is always accessible, prominent, and easy to use.
- **Backgrounds & Visual Details**: Keep it clean and elegant. Use subtle borders, soft shadows for elevation (e.g., floating chat windows or tooltips), and clear visual distinction between user and AI message blocks. 

NEVER use generic, unpolished aesthetics or clichéd layouts. Interpret creatively but within the boundaries of a professional ERP system.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Elegance comes from executing the vision well. Ensure the code is production-grade, highly modular, and strictly follows the technical constraints.

Remember: You are creating an exceptional, robust interface for the ERP Evol. Commit fully to a distinctive, highly functional vision.