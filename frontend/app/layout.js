
import '@/styles/globals.css';
import SWRProvider from '@/components/SWRProvider'; // Import the provider
import Layout from "@/components/Layout";
//import { Toaster } from "@/components/ui/toaster"; // for notifications


export const metadata = {
  title: 'LMS App',
  description: 'LMS for free education',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <SWRProvider> {/* <-- Wrap children with the SWR Provider */}
          <Layout>
            {children}
          </Layout>
        </SWRProvider>
      </body>
    </html>
  );
}
