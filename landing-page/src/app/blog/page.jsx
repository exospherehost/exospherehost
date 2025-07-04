'use client';

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import Link from 'next/link';
import Image from 'next/image';
import Navbar from '@/components/Navbar';
import { darkerGrotesque, pattanakarn } from '@/lib/fonts';
import Footer from '@/components/Footer';

export default function BlogPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch posts from your API endpoint
    const fetchPosts = async () => {
      try {
        const response = await fetch('/api/posts');
        console.log(response);
        const data = await response.json();
        setPosts(data);
      } catch (error) {
        console.error('Error fetching posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const isOdd = posts.length % 2 !== 0;

  if (loading) {
    return (
      <div className="relative min-h-screen bg-[#031035] overflow-hidden">
        <Navbar />
        <div className="flex items-center justify-center h-screen">
          <div className="text-white">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[#031035] overflow-hidden">
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#031035] to-transparent" />

      {/* Navbar */}
      <Navbar />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-18">
        <div className="mb-16 max-w-3xl mx-auto text-center">
          <h1 className={`${pattanakarn.className} text-5xl text-white mb-4`}>exosphere blog</h1>
          <p className={`${darkerGrotesque.className} text-xl text-white/80 font-medium neon-text`}>
            Insights, trends, and perspectives on AI and async computing.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-12">
          {isOdd && posts.length > 0 && (
            <Link 
              key={posts[0].slug}
              href={`/blog/${posts[0].slug}`}
              className="group md:col-span-2"
            >
              <div className="relative rounded-2xl overflow-hidden bg-white/10 backdrop-blur-lg transition-all duration-300 group-hover:shadow-lg group-hover:-translate-y-1">
                {/* Image with dark overlay */}
                <div className="relative h-100 w-full">
                  <Image 
                    src={posts[0].coverImage || '/blog-placeholder.jpg'} 
                    alt={posts[0].title}
                    fill
                    className="object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#031035]/90 via-[#031035]/70 to-[#031035]/0" />
                </div>
                {/* Card Content */}
                <div className="absolute inset-0 flex flex-col justify-end p-8 z-10">
                  <div className={`${darkerGrotesque.className} flex items-center text-xl text-[#daf5ff] mb-3`}>
                    <span>{new Date(posts[0].date).toLocaleDateString('en-US', { 
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}</span>
                    <span className="mx-2">•</span>
                    <span>{posts[0].author}</span>
                  </div>
                  <p className={`${darkerGrotesque.className} text-white/80 mb-4 line-clamp-2`}>{posts[0].excerpt}</p>
                  <h3 className={`${pattanakarn.className} text-2xl font-normal mb-3 text-white lowercase group-hover:text-[#8DE0FF] transition-colors`}>
                    {posts[0].title}
                  </h3>
                  
                  <span className="text-[#8DE0FF] font-medium inline-flex items-center group-hover:translate-x-1 transition-transform">
                    Read more 
                    <svg className="w-4 h-4 ml-1" viewBox="0 0 24 24" fill="none">
                      <path d="M13.75 6.75L19.25 12L13.75 17.25" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M19 12H4.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </span>
                </div>
              </div>
            </Link>
          )}
          {(isOdd ? posts.slice(1) : posts).map((post, idx) => (
            <Link 
              key={post.slug} 
              href={`/blog/${post.slug}`}
              className="group"
            >
              <div className="relative rounded-2xl overflow-hidden bg-white/10 backdrop-blur-lg transition-all duration-300 group-hover:shadow-lg group-hover:-translate-y-1">
                {/* Image with dark overlay */}
                <div className="relative h-100 w-full">
                  <Image 
                    src={post.coverImage || '/blog-placeholder.jpg'} 
                    alt={post.title}
                    fill
                    className="object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#031035]/90 via-[#031035]/70 to-[#031035]/0" />
                </div>
                {/* Card Content */}
                <div className="absolute inset-0 flex flex-col justify-end p-8 z-10">
                  <div className={`${darkerGrotesque.className} flex items-center text-xl text-[#daf5ff] mb-3`}>
                    <span>{new Date(post.date).toLocaleDateString('en-US', { 
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}</span>
                    <span className="mx-2">•</span>
                    <span>{post.author}</span>
                  </div>
                  <p className={`${darkerGrotesque.className} text-white/80 mb-4 line-clamp-2`}>{post.excerpt}</p>
                  <h3 className={`${pattanakarn.className} text-2xl font-normal mb-3 text-white lowercase group-hover:text-[#8DE0FF] transition-colors`}>
                    {post.title}
                  </h3>
                  
                  <span className="text-[#8DE0FF] font-medium inline-flex items-center group-hover:translate-x-1 transition-transform">
                    Read more 
                    <svg className="w-4 h-4 ml-1" viewBox="0 0 24 24" fill="none">
                      <path d="M13.75 6.75L19.25 12L13.75 17.25" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M19 12H4.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <Footer />
    </div>
  );
} 