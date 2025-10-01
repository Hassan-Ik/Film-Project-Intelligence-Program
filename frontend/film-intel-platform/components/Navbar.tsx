"use client";

import Link from 'next/link';

import { useRouter } from "next/navigation";

const Navbar: React.FC = () => {
  const router = useRouter();

  return (
    <nav className="bg-gray-900 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex-shrink-0">
            <Link href="/">
              <span className="text-2xl font-extrabold text-indigo-400 drop-shadow-md tracking-wide">
                CineAnalytics
              </span>
            </Link>
          </div>
          <div className="flex space-x-4">
            <Link href="/story-treatment-analyzer">
              <span
                className={`text-gray-300 hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  router.pathname === '/story-treatment-analyzer' ? 'text-indigo-400 border-b-2 border-indigo-400' : ''
                }`}
              >
                Synopsis & Treatment Analyzer
              </span>
            </Link>
            <Link href="/script-analyzer">
              <span
                className={`text-gray-300 hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  router.pathname === '/script-analyzer' ? 'text-indigo-400 border-b-2 border-indigo-400' : ''
                }`}
              >
                Script Analyzer
              </span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;