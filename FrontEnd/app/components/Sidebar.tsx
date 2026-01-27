'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Cloud, BarChart3, History, Info } from 'lucide-react';
import Image from 'next/image';

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Weather', href: '/weather', icon: Cloud },
  { name: 'Statistics', href: '/statistics', icon: BarChart3 },
  { name: 'History', href: '/history', icon: History },
  { name: 'About Us', href: '/about', icon: Info },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col bg-gray-900 py-10 px-5">
      <div className="flex flex-col justify-center items-center px-4 bg-gray-900">
        <Image 
          src="/assets/LOGO.png" 
          alt="Flights On Time" 
          width={200} 
          height={200} 
          className="mb-1"
        />
      </div>
      
      <nav className="flex-1 space-y-2 px-2 py-6">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`group flex items-center px-2 py-2 text-md font-medium rounded-md ${
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <span className="mr-3">
                <item.icon className="w-5 h-5" />
              </span>
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}