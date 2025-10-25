import React from "react";

function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <div className="inline-block mb-4">
            <span className="text-6xl">🛡️</span>
          </div>
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            About TruthGuard
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            An AI-powered fact-verification platform designed to combat misinformation
            in the digital age. We orchestrate cutting-edge LLMs, trusted news APIs,
            and expert feedback to verify claims in near real-time.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {/* Card 1 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              AI-Powered Verification
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Multi-model AI verification with automatic fallback: OpenAI GPT, Google Gemini, and HuggingFace models working together.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">👨‍💼</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Expert Verification
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Verified experts can override AI decisions with badges and credentials, ensuring human oversight.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">🌍</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Global Coverage
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Track trending news across multiple regions and categories with real-time updates from trusted sources.
            </p>
          </div>

          {/* Card 4 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Admin Dashboard
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Comprehensive admin tools to manage users, experts, badges, regions, and content categories.
            </p>
          </div>

          {/* Card 5 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Real-Time Analysis
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Instant fact-checking with confidence scores and source attribution for every claim.
            </p>
          </div>

          {/* Card 6 */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow duration-300 border border-gray-100 dark:border-gray-700">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-bold mb-3 text-gray-900 dark:text-white">
              Transparent & Secure
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              All verifications are logged with complete transparency and source tracking for accountability.
            </p>
          </div>
        </div>

        {/* Technology Stack */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-10 shadow-xl border border-gray-100 dark:border-gray-700 mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center text-gray-900 dark:text-white">
            Built With Modern Technology
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
              <div className="text-3xl mb-2">⚛️</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">React</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Modern UI Framework</p>
            </div>
            <div className="text-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
              <div className="text-3xl mb-2">🐍</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Flask</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Python Backend</p>
            </div>
            <div className="text-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
              <div className="text-3xl mb-2">🎨</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">Tailwind CSS</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">Utility-First Styling</p>
            </div>
            <div className="text-center p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
              <div className="text-3xl mb-2">🔗</div>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">LangChain</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">AI Orchestration</p>
            </div>
          </div>
        </div>

        {/* Mission Statement */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-500 dark:to-purple-500 rounded-2xl p-10 text-white shadow-2xl">
          <h2 className="text-3xl font-bold mb-4 text-center">Our Mission</h2>
          <p className="text-lg text-center max-w-3xl mx-auto leading-relaxed">
            In an era of information overload, TruthGuard stands as a beacon of reliability.
            We're committed to empowering individuals with the tools they need to discern fact
            from fiction, fostering a more informed and resilient society.
          </p>
        </div>

        {/* Footer */}
        <div className="text-center mt-16">
          <p className="text-gray-600 dark:text-gray-400">
            Have feedback or suggestions? We'd love to hear from you at contact.truthguard@gmail.com.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-4">
            © 2025 TruthGuard. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
}

export default About;
