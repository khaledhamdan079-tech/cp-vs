# CP VS Frontend

React + Vite frontend for the Codeforces Contest Challenge Platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. (Optional) Set environment variable:
```
VITE_API_BASE_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

## Build

```bash
npm run build
```

Output will be in the `dist` directory.

## Railway/Static Hosting Deployment

1. Build the project: `npm run build`
2. Deploy the `dist` directory to your hosting service
3. Set `VITE_API_BASE_URL` to your backend URL
