'use client'

import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Shield, Heart, Users, AlertCircle, MessageCircle } from 'lucide-react'

const resources = [
  {
    id: 'cyberbullying-101',
    title: 'Understanding Cyberbullying',
    description: 'Learn what cyberbullying is, common tactics, and how to recognize it in your online interactions.',
    category: 'Education',
    icon: AlertCircle,
    readTime: '5 min read',
  },
  {
    id: 'protect-privacy',
    title: 'Protecting Your Digital Privacy',
    description: 'Essential tips for keeping your personal information secure online and managing your digital footprint.',
    category: 'Safety Tips',
    icon: Shield,
    readTime: '7 min read',
  },
  {
    id: 'mental-health',
    title: 'Mental Health & Recovery',
    description: 'Resources for emotional support and coping strategies after experiencing online harassment or bullying.',
    category: 'Support',
    icon: Heart,
    readTime: '6 min read',
  },
  {
    id: 'social-media-safety',
    title: 'Social Media Safety Guide',
    description: 'Platform-specific safety tips for popular social media networks and how to adjust privacy settings.',
    category: 'Education',
    icon: Users,
    readTime: '8 min read',
  },
  {
    id: 'reporting-evidence',
    title: 'How to Gather Evidence Safely',
    description: 'Best practices for documenting incidents without putting yourself at risk or compromising investigations.',
    category: 'Safety Tips',
    icon: BookOpen,
    readTime: '5 min read',
  },
  {
    id: 'getting-support',
    title: 'Getting Support & Legal Options',
    description: 'Information about legal remedies, law enforcement involvement, and organizations that can help.',
    category: 'Support',
    icon: MessageCircle,
    readTime: '9 min read',
  },
]

const emergencyContacts = [
  {
    title: 'TrustLine Support',
    phone: '1-800-TRUSTLINE',
    email: 'help@trustline.gov.lk',
    available: '24/7',
  },
  {
    title: 'National Crisis Hotline',
    phone: '1-800-273-8255',
    email: 'crisis@support.org',
    available: '24/7',
  },
  {
    title: 'Cybercrime Police Unit',
    phone: '011-2-123-456',
    email: 'cybercrime@police.lk',
    available: 'Business Hours',
  },
]

export default function ResourcesPage() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
        {/* Hero */}
        <section className="bg-gradient-to-r from-slate-900 to-slate-800 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-4xl font-bold mb-4">Safety & Education Hub</h1>
            <p className="text-xl text-slate-300 max-w-3xl">
              Learn how to protect yourself online and understand your options if you've experienced cyberbullying or harassment.
            </p>
          </div>
        </section>

        {/* Resources Grid */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="text-3xl font-bold text-slate-900 mb-12">Educational Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resources.map((resource) => {
              const Icon = resource.icon
              return (
                <Link key={resource.id} href={`/resources/${resource.id}`}>
                  <Card className="h-full hover:border-cyan-300 transition-colors cursor-pointer">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-2">
                        <Icon className="w-8 h-8 text-cyan-600" />
                        <Badge variant="secondary">{resource.category}</Badge>
                      </div>
                      <CardTitle className="text-lg">{resource.title}</CardTitle>
                      <CardDescription>{resource.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-xs text-slate-500">{resource.readTime}</p>
                    </CardContent>
                  </Card>
                </Link>
              )
            })}
          </div>
        </section>

        {/* Emergency Contacts */}
        <section className="bg-white border-y border-slate-200 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-slate-900 mb-12">Emergency Contacts</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {emergencyContacts.map((contact, index) => (
                <Card key={index} className="border border-red-200 bg-red-50">
                  <CardHeader>
                    <CardTitle className="text-lg text-red-900">{contact.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <p className="text-sm text-slate-600 font-medium">Phone</p>
                      <p className="text-lg font-bold text-red-600">{contact.phone}</p>
                    </div>
                    <div>
                      <p className="text-sm text-slate-600 font-medium">Email</p>
                      <a href={`mailto:${contact.email}`} className="text-cyan-600 hover:text-cyan-700 font-medium">
                        {contact.email}
                      </a>
                    </div>
                    <div>
                      <Badge className="bg-red-600">{contact.available}</Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Safety Tips Highlights */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="text-3xl font-bold text-slate-900 mb-12">Quick Safety Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                title: 'Do Not Engage',
                description: 'Don\'t respond to bullying messages. Responses often escalate the situation.'
              },
              {
                title: 'Screenshot Everything',
                description: 'Take screenshots of harassment before it\'s deleted. This is crucial evidence.'
              },
              {
                title: 'Adjust Privacy Settings',
                description: 'Make your profiles private and control who can contact you and see your content.'
              },
              {
                title: 'Report & Block',
                description: 'Use platform reporting tools and block users. Platform teams take these reports seriously.'
              },
              {
                title: 'Talk to Someone',
                description: 'Reach out to a trusted friend, family member, or counselor. You\'re not alone.'
              },
              {
                title: 'Keep Records',
                description: 'Document dates, times, and details of incidents in a safe place for future reference.'
              }
            ].map((tip, index) => (
              <Card key={index} className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg">{tip.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-600">{tip.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-cyan-50 border-y border-cyan-200 py-12">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-slate-900 mb-6">Need Immediate Help?</h2>
            <p className="text-lg text-slate-700 mb-8">
              Our 24/7 chatbot support team is ready to help you report incidents and provide guidance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/chatbot"
                className="inline-flex items-center justify-center px-6 py-3 bg-cyan-600 text-white font-medium rounded-lg hover:bg-cyan-700 transition-colors"
              >
                Start a Report
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-6 py-3 border-2 border-cyan-600 text-cyan-600 font-medium rounded-lg hover:bg-cyan-50 transition-colors"
              >
                Track Existing Report
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  )
}
