import type { Metadata } from 'next';
import 'bootstrap/dist/css/bootstrap-grid.min.css';
import './globals.css';
export const metadata: Metadata = {title:'Nhà Mình · Quản lý điện nước',description:'Theo dõi điện, nước và hóa đơn của gia đình. Hiểu mức sử dụng với trợ lý thông minh.'};
export default function RootLayout({children}:{children:React.ReactNode}) {return <html lang="vi"><body>{children}</body></html>}
