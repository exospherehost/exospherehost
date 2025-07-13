import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { pattanakarn, darkerGrotesque } from '@/lib/fonts';

interface BlogPost {
  slug: string;
  title: string;
  date: string;
  author: string;
  excerpt: string;
  coverImage: string;
}

export default function BlogSection() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch only the latest 3 blog posts
    const fetchPosts = async () => {
      try {
        const response = await fetch('/api/posts');
        const data = await response.json();
        setPosts(data.slice(0, 3)); // Only get latest 3 posts
      } catch (error) {
        console.error('Error fetching posts:', error);
        // Set fallback post if fetch fails
        setPosts([{
          slug: 'why-exosphere',
          title: 'Your checklist for better sleep',
          date: '2025-04-15',
          author: 'Exosphere Team',
          excerpt: 'Discover how to improve your sleep quality with these simple tips.',
          coverImage: '/images/why-exosphere.jpg'
        }]);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading || posts.length === 0) {
    return null; // Don't show anything while loading
  }

  // Format the date nicely
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="relative w-full flex flex-col items-center justify-center py-16 gap-2 pb-16">
      <h3 className={`${pattanakarn.className} text-center text-2xl text-white mb-2`}>keep reading from our blog</h3>
      <p className={`${darkerGrotesque.className} text-center text-xl text-blue-200 mb-6 max-w-2xl`}>
        Stay updated with the latest insights from our blog
      </p>
      
      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-6 px-4">
        {/* Featured post - larger size */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="col-span-1 md:col-span-2"
        >
          <Link href={`/blog/${posts[0].slug}`} className="group block">
            <div className="relative w-full h-96 overflow-hidden rounded-xl">
              <Image 
                src={posts[0].coverImage || "/images/why-exosphere.jpg"}
                alt={posts[0].title}
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#031035]/95 via-[#031035]/70 to-transparent" />
              <div className="absolute bottom-0 left-0 p-6 w-full">
              <p className={`${darkerGrotesque.className} text-sm text-white/70 line-clamp-2 mb-2`}>
                    {posts[0].excerpt}
                  </p>
                <h3 className={`${darkerGrotesque.className} text-2xl font-bold text-white mb-2 group-hover:text-blue-300 transition-colors`}>
                  {posts[0].title}
                </h3>
                
                
              </div>
            </div>
          </Link>
        </motion.div>
        
        {/* Smaller posts */}
        {posts.slice(1).map((post, index) => (
          <motion.div 
            key={post.slug}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 * (index + 1) }}
          >
            <Link href={`/blog/${post.slug}`} className="group block">
              <div className="relative w-full h-72 overflow-hidden rounded-xl">
                <Image 
                  src={post.coverImage || "/images/why-exosphere.jpg"}
                  alt={post.title}
                  fill
                  className="object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#031035]/95 via-[#031035]/80 to-transparent" />
                <div className="absolute bottom-0 left-0 p-6 w-full">
                <p className={`${darkerGrotesque.className} text-sm text-white/70 line-clamp-2 mb-2`}>
                    {post.excerpt}
                  </p>
                  <h3 className={`${darkerGrotesque.className} text-xl font-bold text-white mb-2 group-hover:text-blue-300 transition-colors`}>
                    {post.title}
                  </h3>
                  
                  
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    
      <div className="mt-8">
        <Link href="/blog" className={`${darkerGrotesque.className} inline-flex h-14 items-center justify-center rounded-xl bg-slate-950 px-6 py-2 text-base font-medium text-white backdrop-blur-3xl border border-transparent hover:border-blue-600/30 transition-colors`}>
          View All Articles
        </Link>
      </div>
    </div>
  );
} 