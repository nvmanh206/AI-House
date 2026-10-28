import type { NextConfig } from 'next';
const config: NextConfig = {output: 'standalone', poweredByHeader: false,
  distDir: process.env.NEXT_DIST_DIR ?? '.next',
  async rewrites(){
    const upstream=process.env.INTERNAL_API_URL||'http://127.0.0.1:8000';
    return [{source:'/api/:path*',destination:`${upstream}/api/:path*`}];
  }};
export default config;
