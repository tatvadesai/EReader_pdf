# PDF E-Reader MVP

## Overview

This is a minimal web-based e-reader application designed for viewing scanned PDF books. The application is built as a single-page application using vanilla web technologies, focusing on simplicity and a clean reading experience. It operates entirely in the browser without requiring a server backend, using browser localStorage for data persistence.

## System Architecture

### Frontend Architecture
- **Technology Stack**: HTML5, CSS3, Vanilla JavaScript
- **PDF Processing**: PDF.js library (v3.11.174) for rendering PDF documents
- **Storage**: Browser localStorage for persisting uploaded PDFs and user preferences
- **Deployment**: Single HTML file with embedded CSS and JavaScript for maximum portability

### Client-Side Only Design
The application follows a client-side only architecture pattern to eliminate server dependencies and simplify deployment. This approach provides:
- Immediate usability without setup
- Privacy (files never leave the user's device)
- Offline functionality
- Easy distribution as a single file

## Key Components

### 1. File Upload System
- Handles PDF file uploads through HTML file input and drag-and-drop interface
- Validates file type (PDF only) and size (50MB limit)
- Converts uploaded files to base64 for localStorage storage
- Generates unique book identifiers for library management

### 2. PDF Renderer
- Utilizes PDF.js library for cross-browser PDF rendering
- Implements canvas-based page rendering for optimal performance
- Features page caching system (current page + next 2 pages) for smooth navigation
- Maintains aspect ratio with auto-fit functionality

### 3. Navigation System
- State management for current page tracking
- Multiple navigation methods: keyboard controls, touch gestures, page input
- Visual progress indication through progress bar
- Smooth page transitions with slide animations

### 4. Reading Interface
- Full-screen reading mode for distraction-free experience
- Multiple zoom options (fit-width, fit-height, custom zoom levels)
- Responsive design optimized for both desktop and mobile devices
- Auto-hiding UI controls for immersive reading

### 5. Book Library
- Grid-based library view displaying book covers (generated from first page)
- Book metadata management (title, page count, last read position)
- Recently opened books tracking
- Simple book deletion functionality

## Data Flow

1. **File Upload**: User selects PDF → File validation → Base64 conversion → localStorage storage
2. **Library Display**: Retrieve stored books → Generate thumbnails → Display in grid layout
3. **Book Opening**: Select book → Load from localStorage → Initialize PDF.js → Render first page
4. **Reading**: Page navigation triggers → Cache management → Canvas rendering → UI updates
5. **State Persistence**: Reading progress and preferences automatically saved to localStorage

## External Dependencies

### PDF.js Library
- **Source**: CDN hosted version (cdnjs.cloudflare.com)
- **Version**: 3.11.174
- **Purpose**: Cross-browser PDF parsing and rendering
- **Integration**: Script tag inclusion with global PDF object access

### Browser APIs
- **File API**: For handling file uploads and reading
- **Canvas API**: For PDF page rendering
- **localStorage API**: For data persistence
- **Touch Events**: For mobile gesture support

## Deployment Strategy

### Single File Distribution
The application is designed as a self-contained HTML file with embedded assets:
- All CSS styles included in `<style>` tags
- All JavaScript code embedded in `<script>` tags
- External dependencies loaded via CDN
- No build process or bundling required

### Hosting Options
- Can be served from any web server
- Compatible with static hosting services
- Works locally when opened in browser (file:// protocol)
- No server-side configuration needed

## Changelog
- June 28, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.