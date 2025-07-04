import { getAllPostSlugs, getPostData } from '@/utils/markdown';
import Image from 'next/image';
import Link from 'next/link';
import { pattanakarn, darkerGrotesque } from '@/lib/fonts';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export async function generateStaticParams() {
  const paths = getAllPostSlugs();
  return paths;
}

export default async function BlogPostPage({ params }) {
  const {slug} = await params;
  const post = await getPostData(slug);  
  return (
    <div className="relative min-h-screen bg-[#031035] overflow-hidden text-[#8DE0FF]">
      {/* Gradient Overlay */}
      
      {/* Navbar */}
      <Navbar />      
      
      <article className="relative z-10 max-w-4xl mx-auto px-4 py-16">
        <header className="mb-12">
          <div className={`${darkerGrotesque.className} flex items-center text-xl text-[#8DE0FF] mb-4`}>
            <span>{new Date(post.date).toLocaleDateString('en-US', { 
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}</span>
            <span className="mx-2">•</span>
            <span>{post.author}</span>
          </div>
          <h1 className={`${pattanakarn.className} text-5xl font-normal leading-tight lowercase text-white mb-6`}>{post.title}</h1>
          <p className={`${darkerGrotesque.className} text-xl text-white neon-text`}>{post.excerpt}</p>
        </header>
        
        <div className="relative h-[500px] w-full mb-12 rounded-xl overflow-hidden border border-white/20">
          <Image 
            src={post.coverImage || '/blog-placeholder.jpg'} 
            alt={post.title}
            fill
            className="object-cover"
            priority
          />
        </div>
        
        <div 
          className={`${darkerGrotesque.className} prose prose-2xl max-w-none mb-10 prose-headings:font-pattanakarn prose-headings:font-normal prose-headings:text-[#8DE0FF] prose-p:text-white prose-a:text-[#8DE0FF] prose-a:no-underline hover:prose-a:text-[#8DE0FF]/80 prose-strong:text-white prose-strong:font-medium prose-strong:font-pattanakarn prose-strong:text-xl prose-strong:block prose-strong:mb-4 prose-strong:mt-8 prose-strong:leading-relaxed prose-strong:tracking-wide prose-strong:uppercase prose-strong:letter-spacing-0.05em prose-strong:text-[#8DE0FF] [&_li]:text-[#daf5ff] [&_ul]:text-[#daf5ff] [&_ol]:text-[#daf5ff]`}
          dangerouslySetInnerHTML={{ __html: post.contentHtml }}
        />
        
        <div className="border-t border-white/20 pt-12">
          <div className="flex items-start">
            <div className="flex-shrink-0 mr-6">
              <div className="h-20 w-20 rounded-full bg-white/10 backdrop-blur-lg flex items-center justify-center border border-white/20">
                <span className={`${pattanakarn.className} text-2xl font-normal text-[#E2CBFF]`}>{post.author.charAt(0)}</span>
              </div>
            </div>
            <div>
              <h3 className={`${pattanakarn.className} text-xl font-normal text-white mb-1`}>{post.author}</h3>
              <p className={`${darkerGrotesque.className} text-xl text-white mb-3`}>{post.authorRole}</p>
              <p className={`${darkerGrotesque.className} text-white text-xl`}>{post.authorBio}</p>
            </div>
          </div>
        </div>
        
        <div className="mt-16 pt-8 border-t border-white/20">
          <Link 
            href="/blog" 
            className="text-[#8DE0FF] font-medium inline-flex items-center hover:-translate-x-1 transition-transform"
          >
            <svg className="w-4 h-4 mr-1 rotate-180" viewBox="0 0 24 24" fill="none">
              <path d="M13.75 6.75L19.25 12L13.75 17.25" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M19 12H4.75" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Back to all articles
          </Link>
        </div>
      </article>
      
      <Footer />
    </div>
  );
} 