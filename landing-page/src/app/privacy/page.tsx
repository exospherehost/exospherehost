"use client"

import Navbar from "@/components/Navbar"
import Stars from "@/components/Stars"
import PulsatingGradient from "@/components/PulsatingGradient"
import Footer from "@/components/Footer"
import FloatingBar from "@/components/FloatingBar"
import { pattanakarn, darkerGrotesque } from "@/lib/fonts"

export default function PrivacyPolicy() {
  return (
    <div className="w-full min-h-screen relative bg-[#031035]">
      <PulsatingGradient />
      {/* Twinkling Stars */}
      <Stars />

      <div className="relative z-100">
        <Navbar />       
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#031035] to-transparent" />

      {/* Content */}
      <div className="relative max-w-4xl mx-auto px-4 py-16 z-10 text-[#8bdfff]">
        <h1 className={`${pattanakarn.className} text-3xl md:text-4xl text-white mb-8 text-center`}>
          Privacy Policy
        </h1>
        
        <div className={`${darkerGrotesque.className} text-white space-y-6 text-lg`}>
        <h2 className="text-2xl text-white mt-8 mb-4">1. Introduction</h2>
        <p>
          At Exosphere, a platform owned and operated by Mathrithms Technologies Pvt Ltd, we are committed to protecting the privacy and confidentiality of our users and clients. This Privacy Policy outlines what data we collect, how we use it, and the rights you have over your data. By using our services, you agree to the terms described here.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">2. Information We Collect</h2>
        <p>We collect technical and business information from users who interact with our platform.</p>

        <p><strong>User Data:</strong> We may collect the following:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>Contact details (e.g., name, email)</li>
          <li>Job metadata and workflow configurations</li>
          <li>API usage logs and system interaction history</li>
          <li>Billing and account preferences</li>
        </ul>

        <p><strong>Client Data:</strong> If you’re a paying customer or enterprise user, we also collect:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>Company name and authorized contact information</li>
          <li>Cloud infrastructure configurations, if shared with us</li>
          <li>Deployment and performance preferences for workload optimization</li>
        </ul>

        <h2 className="text-2xl text-white mt-8 mb-4">3. Use of Information</h2>
        <p>We use your data to:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>Deliver, optimize, and troubleshoot our orchestration services</li>
          <li>Recommend workload improvements and SLA-based tuning</li>
          <li>Enable integrations with external tools like S3, GitHub, or Compute Backends</li>
          <li>Contact you about updates, system incidents, or service-related notices</li>
        </ul>

        <h2 className="text-2xl text-white mt-8 mb-4">4. Data Security</h2>
        <p>
          We host all user and job data on secure cloud infrastructure with:
        </p>
        <ul className="list-disc list-inside space-y-2">
          <li>Data encryption at rest and in transit</li>
          <li>Role-based access control and audit logging</li>
          <li>Regular security patches and vulnerability scans</li>
        </ul>

        <h2 className="text-2xl text-white mt-8 mb-4">5. Data Sharing and Access</h2>
        <p>
          Your data is shared only under the following conditions:
        </p>
        <ul className="list-disc list-inside space-y-2">
          <li>With trusted cloud vendors and processors under strict NDAs</li>
          <li>With internal team members for support, optimization, or debugging</li>
          <li>When required by law or valid legal request</li>
        </ul>
        <p>
          We do not sell or rent your data to third parties. Data shared for SLA fulfillment or optimization is anonymized where possible.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">6. Data Retention</h2>
        <p>
          We retain user and job data for 12 months from the date of last activity unless otherwise required for support, billing, or legal compliance. You can request earlier deletion by contacting us.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">7. Cookies and Tracking</h2>
        <p>
          Exosphere uses cookies only to maintain login sessions and authentication tokens. We do not use tracking for advertising. Anonymous analytics may be used to improve user experience and performance.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">8. Data Deletion</h2>
        <p>
          You can request deletion of your data at any time by emailing hello@exosphere.dev. We will process such requests within a reasonable timeframe and confirm once the deletion is complete.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">9. Updates to This Policy</h2>
        <p>
          We may update this Privacy Policy periodically. If changes are significant, we will notify you via email or platform notification. We encourage you to review this policy occasionally to stay informed.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">10. Contact</h2>
        <p>For privacy-related inquiries, data access requests, or general questions, contact us at:</p>
        <p>Email: hello@exosphere.dev</p>
        <p>Phone: +91-8474985454</p>
        <p>Address: B-1/32 Adarsh Gram Vasudev Residency, Dehradun Road Behind Andhra Bank, Adarsh Gram, Rishikesh, Uttarakhand (249201), India</p>

        <h2 className="text-2xl text-white mt-8 mb-4">11. Legal Information</h2>
        <p>Exosphere is a product of Mathrithms Technologies Pvt Ltd</p>
        <p>CIN: U72900UR2022PTC013816</p>
        <p>GSTIN: 05AAPCM6346R1ZL</p>
        </div>
      </div>

      {/* Footer */}
      <div className="relative">
        <Footer />
      </div>

      {/* Floating Social Bar */}
      <FloatingBar />
    </div>
  )
} 