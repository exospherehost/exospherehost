"use client"

import Navbar from "@/components/Navbar"
import Stars from "@/components/Stars"
import PulsatingGradient from "@/components/PulsatingGradient"
import Footer from "@/components/Footer"
import FloatingBar from "@/components/FloatingBar"
import { pattanakarn, darkerGrotesque } from "@/lib/fonts"

export default function TermsAndConditions() {
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
          Terms and Conditions
        </h1>
        
        <div className={`${darkerGrotesque.className} text-white space-y-6 text-lg`}>
          <p>Last Updated: {new Date().toLocaleDateString()}</p>

          

        <h2 className="text-2xl text-white mt-8 mb-4">1. Introduction</h2>
        <p>
          These Terms and Conditions (“Terms”) govern your access to and use of the services offered by Exosphere, a platform developed and operated by Mathrithms Technologies Pvt Ltd (“Exosphere,” “we,” “our,” or “us”). By accessing or using our website, APIs, software, or services (collectively, “Services”), you agree to these Terms. If you do not agree, you may not use the Services.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">2. Definitions</h2>
        <p><strong>Website</strong>: Refers to the Exosphere platform accessible at www.exosphere.dev.</p>
        <p><strong>Services</strong>: Includes, but is not limited to, job orchestration APIs, AI model deployments, workflow automation, SLAs, storage integrations, SDKs, and developer tools provided through Exosphere.</p>
        <p><strong>User</strong>: Refers to individuals or organizations using the Exosphere platform.</p>
        <p><strong>Client</strong>: Refers to any organization or individual who subscribes to Exosphere’s paid plans or custom integrations.</p>
        <p><strong>Jobs</strong>: Refers to individual AI tasks, workflows, or batch processes submitted via Exosphere.</p>
        <p><strong>SLA</strong>: Service-level agreement regarding uptime, job execution timelines, or retries as configured within the platform.</p>

        <h2 className="text-2xl text-white mt-8 mb-4">3. Acceptance of Terms</h2>
        <p>
          By accessing or using Exosphere, you agree to be legally bound by these Terms. If you are acting on behalf of a company or other entity, you represent and warrant that you have the authority to bind such entity to these Terms.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">4. Services Provided</h2>
        <p>
          Exosphere provides infrastructure and APIs to orchestrate background jobs, batch inference workloads, and multistep AI workflows. Key features include:
        </p>
        <ul className="list-disc list-inside space-y-2">
          <li>Submission and tracking of AI/ML workloads</li>
          <li>Integration with storage (e.g., S3, GCS) and compute backends</li>
          <li>SLA definition and automated job retries</li>
          <li>Webhooks, SDKs, and REST APIs for automation</li>
          <li>Multi-cloud and on-prem compute orchestration</li>
        </ul>
        <p>Some features may require payment or subscription, which will be governed by separate pricing agreements.</p>

        <h2 className="text-2xl text-white mt-8 mb-4">5. User Responsibilities</h2>
        <p>You agree to:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>Provide accurate account and billing information</li>
          <li>Use the platform only for lawful, ethical, and authorized purposes</li>
          <li>Not interfere with or disrupt the Services or servers</li>
          <li>Respect all intellectual property rights associated with Exosphere’s software and platform</li>
          <li>Not attempt to reverse engineer, decompile, or otherwise misuse the platform</li>
        </ul>

        <h2 className="text-2xl text-white mt-8 mb-4">6. Data Privacy</h2>
        <p>
          By using Exosphere, you acknowledge and agree that we may collect and use your data as outlined in our Privacy Policy. You retain ownership of your data and jobs, but grant us limited rights to process, store, and optimize workflows on your behalf.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">7. API Usage and Fair Use</h2>
        <p>
          You may access Exosphere services via APIs and SDKs, subject to rate limits and fair use thresholds. Abuse, excessive use, or automated scraping outside documented APIs may result in suspension or termination of access.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">8. Prohibited Activities</h2>
        <p>You agree not to:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>Submit illegal, harmful, or unethical jobs</li>
          <li>Use Exosphere for military, surveillance, or discriminatory purposes</li>
          <li>Bypass metering, pricing logic, or service restrictions</li>
          <li>Introduce malware, unauthorized agents, or mining tools</li>
          <li>Share platform credentials or API tokens with third parties</li>
        </ul>

        <h2 className="text-2xl text-white mt-8 mb-4">9. Service Availability & Liability</h2>
        <p>
          While we strive for maximum reliability, Exosphere does not guarantee uninterrupted service. Exosphere is not liable for:
        </p>
        <ul className="list-disc list-inside space-y-2">
          <li>Job failures due to external dependencies</li>
          <li>Data loss or corruption</li>
          <li>Downstream impact of incorrect or incomplete job outputs</li>
          <li>Financial or reputational losses from reliance on results generated through the platform</li>
        </ul>
        <p>
          Maximum liability is limited to the fees paid for the impacted service during the prior 30-day period.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">10. Termination</h2>
        <p>
          We may suspend or terminate access to the Services at any time for violation of these Terms. You may also discontinue use at any time. Upon termination, your data may be deleted after a reasonable retention period unless subject to ongoing obligations.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">11. Changes to Terms</h2>
        <p>
          These Terms may be updated from time to time. Changes will be posted on this page with an updated date. Continued use of the platform after updates indicates acceptance of the revised Terms.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">12. Governing Law</h2>
        <p>
          These Terms shall be governed by the laws of India. Any disputes shall be resolved via arbitration in Dehradun, Uttarakhand, India, in accordance with Indian law.
        </p>

        <h2 className="text-2xl text-white mt-8 mb-4">13. Contact Information</h2>
        <p>Email: hello@exosphere.dev</p>
        <p>Phone: +91-8474985454</p>
        <p>Address: B-1/32 Adarsh Gram Vasudev Residency, Dehradun Road Behind Andhra Bank, Adarsh Gram, Rishikesh, Uttarakhand (249201), India</p>       
          

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