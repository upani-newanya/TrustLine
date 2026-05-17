'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { isAuthenticated, getStoredRole } from '@/lib/auth'
import { Shield, MessageCircle, Lock, Users, Zap, Heart } from 'lucide-react'

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setIsLoggedIn(isAuthenticated())
  }, [])

  const handleReportClick = () => {
    if (isLoggedIn) {
      router.push('/chatbot')
    } else {
      router.push('/login')
    }
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center space-y-8">
            <div className="flex justify-center">
              <div className="bg-cyan-100 p-4 rounded-full">
                <Shield className="w-12 h-12 text-cyan-600" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-slate-900">
              Report Cyberbullying.
              <br />
              <span className="text-cyan-600">Protect Your Privacy.</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              TrustLine provides a secure, confidential platform for victims of cyberbullying, online harassment, and privacy violations to report incidents and get support 24/7.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Button
                size="lg"
                onClick={handleReportClick}
                className="bg-cyan-600 hover:bg-cyan-700 text-white"
              >
                Report Now
              </Button>
              <Button
                size="lg"
                variant="outline"
                asChild
              >
                <Link href="/resources">Learn More</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="bg-white py-16 border-y border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[
                {
                  step: '1',
                  title: 'Chat with Support',
                  description: 'Talk to our AI-powered chatbot that provides guidance and support 24/7'
                },
                {
                  step: '2',
                  title: 'File Your Report',
                  description: 'Share details about the incident and upload evidence securely'
                },
                {
                  step: '3',
                  title: 'Get a Case ID',
                  description: 'Receive a unique case ID to track your report status'
                },
                {
                  step: '4',
                  title: 'Professional Review',
                  description: 'Trained cybercrime specialists review and investigate your case'
                }
              ].map((item) => (
                <div key={item.step} className="text-center">
                  <div className="bg-cyan-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-cyan-600 text-lg">
                    {item.step}
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-2">{item.title}</h3>
                  <p className="text-slate-600 text-sm">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">Why Choose TrustLine?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: Lock,
                  title: 'Secure & Confidential',
                  description: 'Your data is encrypted and protected. Report anonymously if you choose.'
                },
                {
                  icon: Zap,
                  title: '24/7 Support',
                  description: 'Our AI chatbot is available round the clock to provide immediate support and guidance.'
                },
                {
                  icon: Users,
                  title: 'Expert Review',
                  description: 'Trained cybercrime specialists investigate every report with care and professionalism.'
                },
                {
                  icon: Heart,
                  title: 'Victim Support',
                  description: 'Access resources, safety tips, and mental health support during your recovery.'
                },
                {
                  icon: MessageCircle,
                  title: 'Direct Messaging',
                  description: 'Communicate securely with investigators and receive case updates in real time.'
                },
                {
                  icon: Shield,
                  title: 'Legal Support',
                  description: 'Get guidance on legal options and assistance with evidence preservation.'
                }
              ].map((feature, index) => {
                const Icon = feature.icon
                return (
                  <Card key={index} className="border border-slate-200 hover:border-cyan-300 transition-colors">
                    <CardHeader>
                      <Icon className="w-8 h-8 text-cyan-600 mb-2" />
                      <CardTitle className="text-lg">{feature.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-slate-600">{feature.description}</p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>
        </section>

        {/* Evidence Supported */}
        <section className="bg-slate-50 py-16 border-y border-slate-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">Evidence We Accept</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {['Screenshots', 'Messages', 'Videos', 'Images', 'Emails', 'Documents', 'Audio Files', 'URLs'].map((type) => (
                <Card key={type} className="text-center border border-slate-200">
                  <CardContent className="pt-6">
                    <p className="font-semibold text-slate-900">{type}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
            <p className="text-center text-slate-600 mt-8 text-sm">
              Maximum file size: 50MB per file. All evidence is securely stored and protected.
            </p>
          </div>
        </section>

        {/* Privacy Promise */}
        <section className="py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-slate-900 mb-8">Our Privacy Promise</h2>
            <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-8 space-y-4">
              <p className="text-slate-700">
                At TrustLine, your privacy and safety are paramount. We promise:
              </p>
              <ul className="text-left space-y-3 max-w-2xl mx-auto">
                <li className="flex gap-3">
                  <span className="text-cyan-600 font-bold">✓</span>
                  <span className="text-slate-700">All reports and evidence are encrypted and securely stored</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-cyan-600 font-bold">✓</span>
                  <span className="text-slate-700">You can report anonymously or use your real identity</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-cyan-600 font-bold">✓</span>
                  <span className="text-slate-700">Your information will never be sold or shared without consent</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-cyan-600 font-bold">✓</span>
                  <span className="text-slate-700">Only authorized personnel can access your report</span>
                </li>
                <li className="flex gap-3">
                  <span className="text-cyan-600 font-bold">✓</span>
                  <span className="text-slate-700">You have full control over your data and can request deletion</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <h2 className="text-3xl font-bold">Ready to Report?</h2>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto">
              Start your report now with our guided chat system. Get support immediately and help us create a safer online community.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Button
                size="lg"
                onClick={handleReportClick}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                Start Report Now
              </Button>
              {!isLoggedIn && (
                <Button
                  size="lg"
                  variant="outline"
                  asChild
                >
                  <Link href="/register">Create Account</Link>
                </Button>
              )}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  )
}
