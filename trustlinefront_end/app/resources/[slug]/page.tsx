'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

const resourceContent = {
  'cyberbullying-101': {
    title: 'Understanding Cyberbullying',
    category: 'Education',
    readTime: '5 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">What is Cyberbullying?</h2>
          <p>
            Cyberbullying is the use of digital platforms and technologies to harass, threaten, embarrass, or target another person. Unlike traditional bullying, cyberbullying can happen 24/7 and can reach a much wider audience.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Common Forms</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Sending hurtful messages via text, email, or social media</li>
            <li>Spreading rumors or sharing embarrassing photos/videos</li>
            <li>Creating fake accounts to impersonate or mock someone</li>
            <li>Excluding someone from online groups or conversations</li>
            <li>Making threats or using intimidating language</li>
            <li>Sharing private or embarrassing information without consent</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Signs You're Being Cyberbullied</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Receiving hurtful messages or comments online</li>
            <li>Being excluded from online groups or conversations</li>
            <li>Seeing rumors or false information about you spreading online</li>
            <li>Receiving threats or intimidating messages</li>
            <li>Having embarrassing photos or videos shared without permission</li>
          </ul>
        </section>

        <section className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-3">What You Can Do</h3>
          <ol className="space-y-2 list-decimal list-inside">
            <li>Don't respond to the bully - responses often make things worse</li>
            <li>Save evidence - take screenshots of messages and posts</li>
            <li>Block the person on social media and messaging apps</li>
            <li>Report the behavior to the platform</li>
            <li>Tell a trusted adult - parent, teacher, or counselor</li>
            <li>Report to TrustLine for investigation and support</li>
          </ol>
        </section>
      </div>
    )
  },
  'protect-privacy': {
    title: 'Protecting Your Digital Privacy',
    category: 'Safety Tips',
    readTime: '7 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Your Digital Footprint</h2>
          <p>
            Everything you post, like, or share online creates a digital footprint. This information can be used by others and may persist even after you delete it. Taking control of your digital footprint is essential for protecting your privacy.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Privacy Settings Checklist</h2>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Social Media</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 list-disc list-inside text-sm">
                  <li>Set your profile to private</li>
                  <li>Only accept friend requests from people you know</li>
                  <li>Limit who can comment on your posts</li>
                  <li>Disable location services</li>
                  <li>Review tagged photos before they appear on your profile</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Strong Passwords</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Use at least 12 characters with a mix of uppercase, lowercase, numbers, and symbols</li>
            <li>Use unique passwords for important accounts</li>
            <li>Enable two-factor authentication when available</li>
            <li>Never share your password with anyone</li>
            <li>Change passwords regularly, especially if you think an account has been compromised</li>
          </ul>
        </section>

        <section className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-3">Personal Information to Protect</h3>
          <p className="mb-3">Never share the following online:</p>
          <ul className="space-y-1 list-disc list-inside">
            <li>Your full name and date of birth</li>
            <li>Your home address or school name</li>
            <li>Your phone number or email address (use separate email for less important accounts)</li>
            <li>Your schedule or location information</li>
            <li>Financial information or credit card numbers</li>
          </ul>
        </section>
      </div>
    )
  },
  'mental-health': {
    title: 'Mental Health & Recovery',
    category: 'Support',
    readTime: '6 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Impact of Online Harassment</h2>
          <p>
            Being targeted online can have serious effects on your mental health and wellbeing. It's important to acknowledge these feelings and seek support. You are not alone, and help is available.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Common Emotional Responses</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Anxiety or fear about checking messages or social media</li>
            <li>Depression or feelings of hopelessness</li>
            <li>Shame or embarrassment about what others have said</li>
            <li>Anger or frustration about the situation</li>
            <li>Difficulty concentrating at school or work</li>
            <li>Sleep problems or changes in appetite</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Self-Care Strategies</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'Take a Break', description: 'Step away from social media and online spaces for a while' },
              { title: 'Reach Out', description: 'Talk to friends, family, or a counselor about what you\'re experiencing' },
              { title: 'Exercise', description: 'Physical activity helps reduce stress and improve mood' },
              { title: 'Journal', description: 'Write about your feelings to process emotions' },
              { title: 'Practice Mindfulness', description: 'Meditation and breathing exercises can help with anxiety' },
              { title: 'Set Boundaries', description: 'Limit time online and mute notifications' }
            ].map((item, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-base">{item.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm">{item.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-3">Professional Help</h3>
          <p className="mb-3">
            If you're struggling with thoughts of self-harm or suicide, please reach out immediately:
          </p>
          <ul className="space-y-2 list-disc list-inside">
            <li>National Crisis Hotline: 1-800-273-8255 (24/7)</li>
            <li>Text HELLO to 741741</li>
            <li>Talk to a school counselor, therapist, or doctor</li>
          </ul>
        </section>
      </div>
    )
  },
  'social-media-safety': {
    title: 'Social Media Safety Guide',
    category: 'Education',
    readTime: '8 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Platform-Specific Safety</h2>
          <p>
            Each social media platform has different safety features and risks. Understanding how to use these features effectively can help protect you from cyberbullying.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Instagram</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Go to Settings → Privacy to control who can contact you</li>
            <li>Restrict accounts to limit their ability to see your content</li>
            <li>Use Close Friends feature to share posts with select people</li>
            <li>Review tagged posts before they appear on your profile</li>
            <li>Report abusive comments or messages immediately</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">TikTok</h2>
          <ul className="space-y-2 list-disc list-inside">
            <li>Set your account to Private to control who can see your videos</li>
            <li>Manage who can comment on your videos</li>
            <li>Use the Duet and Stitch features selectively</li>
            <li>Block users who are harassing you</li>
            <li>Report content that violates community guidelines</li>
          </ul>
        </section>

        <section className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-3">General Social Media Safety Tips</h3>
          <ul className="space-y-2 list-disc list-inside">
            <li>Don't accept friend requests from strangers</li>
            <li>Be careful about what you post - think before sharing</li>
            <li>Review privacy settings regularly as platforms change</li>
            <li>Don't meet people in person that you only know online</li>
            <li>Report suspicious accounts or behavior</li>
          </ul>
        </section>
      </div>
    )
  },
  'reporting-evidence': {
    title: 'How to Gather Evidence Safely',
    category: 'Safety Tips',
    readTime: '5 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Why Evidence Matters</h2>
          <p>
            Gathering evidence is crucial for reporting cyberbullying effectively. It provides proof of what happened and helps investigators build a case. However, it's important to do this safely and legally.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Types of Evidence to Collect</h2>
          <ul className="space-y-3 list-disc list-inside">
            <li>
              <strong>Screenshots:</strong> Capture the entire message or post, including the sender's name and timestamp
            </li>
            <li>
              <strong>URLs:</strong> Copy and save links to posts, comments, or profiles involved
            </li>
            <li>
              <strong>Metadata:</strong> Include information about when the incident occurred
            </li>
            <li>
              <strong>Contact Details:</strong> Document usernames, profiles, and accounts of the person harassing you
            </li>
            <li>
              <strong>Videos/Media:</strong> Save any videos or images used in the harassment
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Safe Collection Practices</h2>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
            <p className="font-semibold text-slate-900">Do's:</p>
            <ul className="space-y-1 list-disc list-inside text-sm">
              <li>Take screenshots immediately after incidents occur</li>
              <li>Save evidence to your device or cloud storage</li>
              <li>Document the date and time of each incident</li>
              <li>Keep a written log of what happened</li>
              <li>Share evidence with trusted adults or authorities</li>
            </ul>

            <p className="font-semibold text-slate-900 mt-4">Don'ts:</p>
            <ul className="space-y-1 list-disc list-inside text-sm">
              <li>Don't engage with the bully while collecting evidence</li>
              <li>Don't attempt to hack or access private accounts</li>
              <li>Don't share evidence publicly on social media</li>
              <li>Don't alter or manipulate evidence</li>
              <li>Don't confront the person collecting evidence directly</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Uploading to TrustLine</h2>
          <p>
            TrustLine accepts various file types as evidence. When uploading, ensure:
          </p>
          <ul className="space-y-2 list-disc list-inside">
            <li>Files are clear and readable</li>
            <li>All relevant information is visible (including usernames, dates, times)</li>
            <li>File sizes do not exceed 50MB</li>
            <li>You have permission to submit the evidence</li>
          </ul>
        </section>
      </div>
    )
  },
  'getting-support': {
    title: 'Getting Support & Legal Options',
    category: 'Support',
    readTime: '9 min read',
    content: (
      <div className="space-y-6 text-slate-700">
        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">You Are Not Alone</h2>
          <p>
            Cyberbullying and online harassment are serious crimes in many jurisdictions. There are legal options available to you, and professional support services can help you navigate this difficult situation.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Types of Support Available</h2>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Legal Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  Depending on the severity of the harassment, you may be able to pursue legal action, obtain restraining orders, or file police reports. TrustLine can guide you through these options.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Emotional Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  Mental health professionals can help you cope with anxiety, depression, and trauma resulting from online harassment.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Platform Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  Social media platforms have trust and safety teams that investigate reports and can remove content or suspend accounts.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Community Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  Support groups and community organizations can connect you with others who understand what you're experiencing.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Legal Options</h2>
          <ul className="space-y-3 list-disc list-inside">
            <li>
              <strong>Report to Law Enforcement:</strong> File a police report for criminal behavior like threats, stalking, or harassment
            </li>
            <li>
              <strong>Restraining Order:</strong> Request a legal order to prevent the person from contacting you
            </li>
            <li>
              <strong>Civil Suit:</strong> In some cases, you may be able to sue for damages
            </li>
            <li>
              <strong>Platform Reports:</strong> Use the platform's built-in reporting tools to remove content
            </li>
          </ul>
        </section>

        <section className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-3">Next Steps</h3>
          <ol className="space-y-2 list-decimal list-inside">
            <li>Report the incident to TrustLine with evidence</li>
            <li>Document everything and keep it safe</li>
            <li>Talk to a trusted adult - parent, counselor, or teacher</li>
            <li>Consider seeking legal or mental health support</li>
            <li>Follow up regularly on your case</li>
          </ol>
        </section>
      </div>
    )
  }
}

export default function ResourceDetailPage() {
  const params = useParams()
  const slug = params.slug as string
  const resource = resourceContent[slug as keyof typeof resourceContent]

  if (!resource) {
    return (
      <>
        <Navbar />
        <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
          <div className="max-w-4xl mx-auto px-4">
            <Button asChild variant="ghost" className="mb-6">
              <Link href="/resources" className="flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Resources
              </Link>
            </Button>
            <Card>
              <CardContent className="pt-6">
                <p className="text-slate-600">Resource not found</p>
              </CardContent>
            </Card>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <Button asChild variant="ghost" className="mb-6">
            <Link href="/resources" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Resources
            </Link>
          </Button>

          <article className="bg-white rounded-lg shadow-sm p-8 border border-slate-200">
            <div className="mb-8">
              <div className="flex items-center gap-4 mb-4">
                <span className="text-sm font-medium text-cyan-600 bg-cyan-50 px-3 py-1 rounded-full">
                  {resource.category}
                </span>
                <span className="text-sm text-slate-500">{resource.readTime}</span>
              </div>
              <h1 className="text-4xl font-bold text-slate-900">{resource.title}</h1>
            </div>

            <div className="prose prose-slate max-w-none">
              {resource.content}
            </div>
          </article>

          <div className="mt-8 bg-cyan-50 border border-cyan-200 rounded-lg p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-3">Need Help?</h3>
            <p className="text-slate-700 mb-4">
              If you're experiencing cyberbullying or harassment, TrustLine is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
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
                Login to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
