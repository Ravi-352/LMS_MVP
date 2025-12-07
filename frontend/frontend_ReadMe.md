## Step 1: Run this in your frontend directory of project folder:  
```bash
npm init -y

# Install Next + React + utilities
npm install next react react-dom swr
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

This installs styling libraries and generates:

```tailwind.config.js```
```postcss.config.js```

## Step 2 — Configure Tailwind  
Replace the generated tailwind.config.js with:  

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

```
This tells Tailwind to scan your pages and components for class names.


## Step 3 — Add Tailwind base styles
Replace styles/globals.css with:  
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Your custom overrides here */

body {
  @apply bg-gray-50 text-gray-900;
}

.container {
  @apply max-w-6xl mx-auto px-4;
}

```

## Step 4 - Install shadcn/ui and add components - clean UI building blocks

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card textarea input navbar dialog progress
```

### Note points:

Layout --> md:hidden hides element on medium+ screens. So we show hamburger on mobile only
CourseCard: Clean card with CTA styled in the purple primary color.
SidebarLessons:--> md:block --> On small screens this sidebar is hidden — content will be full-width for readability.

### spinning up frontend using docker --
#### Image creation
docker build --build-arg NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1 -t lms-frontend:1.0 .

#### container creation - 
![NOTE]> Avoid saving sensitive secrets like DB urls and secrets in .env.local as nextjs build is partially public and can expose secrets.
docker run -dt -p 3000:3000 --env-file=.env.local lms-frontend:1.0

#### stopping and deleting containers that use the image above
docker stop $(docker ps -aq --filter "ancestor=lms-frontend:1.0")| xargs docker rm



