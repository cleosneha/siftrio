"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";

const EASE = [0.25, 0.1, 0.25, 1] as const;

const SECTIONS = [
  { id: "introduction", label: "Introduction" },
  { id: "information-we-collect", label: "Information We Collect" },
  { id: "how-we-use-information", label: "How We Use Information" },
  { id: "legal-basis", label: "Legal Basis for Processing" },
  { id: "google-account-data", label: "Google Account Data" },
  { id: "third-party-integrations", label: "Third-Party Integrations" },
  { id: "data-storage", label: "Data Storage" },
  { id: "data-sharing", label: "Data Sharing" },
  { id: "data-security", label: "Data Security" },
  { id: "cookies-and-tracking", label: "Cookies and Session Management" },
  { id: "your-rights", label: "Your Rights" },
  { id: "childrens-privacy", label: "Children's Privacy" },
  { id: "changes-to-this-policy", label: "Changes to this Policy" },
  { id: "contact-us", label: "Contact Us" },
];

export default function PrivacyPolicy() {
  const [activeId, setActiveId] = useState(SECTIONS[0].id);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const headings = SECTIONS.map((s) => document.getElementById(s.id)).filter(
      Boolean,
    );

    observerRef.current = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      { rootMargin: "-20% 0px -60% 0px" },
    );

    headings.forEach((el) => {
      if (el) observerRef.current?.observe(el);
    });

    return () => observerRef.current?.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* ── Nav ── */}
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-[820px] items-center justify-between px-6">
          <Link
            href="/"
            className="text-sm text-disabled-text transition-colors hover:text-foreground"
          >
            &larr; Back to Home
          </Link>
          <span className="text-lg font-semibold text-foreground">Siftrio</span>
          <span className="w-[120px]" />
        </div>
      </nav>

      {/* ── Content ── */}
      <div className="mx-auto max-w-[820px] px-6">
        {/* ── Hero ── */}
        <motion.div
          className="pt-24 pb-20"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: EASE }}
        >
          <h1 className="text-[40px] font-semibold leading-tight tracking-tight text-foreground">
            Privacy Policy
          </h1>

          <div className="mt-6 flex gap-10 text-[13px] text-disabled-text">
            <div>
              <span className="block text-subtle-text">Effective Date</span>
              July 17, 2026
            </div>
            <div>
              <span className="block text-subtle-text">Last Updated</span>
              July 22, 2026
            </div>
          </div>

          <p className="mt-10 max-w-[640px] text-[17px] leading-[1.8] text-disabled-text">
            This Privacy Policy explains how Siftrio collects, uses, stores, and
            protects your information when you use our services.
          </p>
        </motion.div>

        {/* ── Table of Contents ── */}
        <motion.div
          className="border-t border-border pb-20 pt-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, ease: EASE, delay: 0.15 }}
        >
          <p className="mb-6 text-[11px] font-medium uppercase tracking-[0.2em] text-subtle-text">
            Contents
          </p>
          <nav className="flex flex-col gap-1">
            {SECTIONS.map((s, i) => (
              <button
                key={s.id}
                onClick={() => scrollTo(s.id)}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-left text-[14px] transition-colors ${
                  activeId === s.id
                    ? "bg-accent text-foreground"
                    : "text-disabled-text hover:text-soft-text"
                }`}
              >
                <span className="w-5 text-right text-[12px] text-faint-text">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {s.label}
              </button>
            ))}
          </nav>
        </motion.div>

        {/* ── Document ── */}
        <div className="border-t border-border pt-20">
          {/* 01 Introduction */}
          <Section id="introduction" number="01" title="Introduction">
            <p>
              Siftrio (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;) is
              committed to protecting your privacy. This Privacy Policy applies
              to all users of our website, applications, and services
              (collectively, the &quot;Services&quot;). By using our Services,
              you agree to the collection and use of information as described in
              this policy.
            </p>
            <p>
              We believe in transparency and want you to understand exactly what
              data we collect, why we collect it, and how it is used. This
              policy is designed to be clear and straightforward. For the terms
              governing your use of the Services, please review our{" "}
              <Link
                href="/terms"
                className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
              >
                Terms &amp; Conditions
              </Link>
              .
            </p>
          </Section>

          {/* 02 Information We Collect */}
          <Section
            id="information-we-collect"
            number="02"
            title="Information We Collect"
          >
            <p>We collect the following types of information:</p>
            <p className="font-medium text-soft-text">Account Information</p>
            <p>
              When you sign in using Google OAuth, we receive your name, email
              address, and profile picture. This information is used solely to
              identify you within the application and to provide our services.
            </p>
            <p className="font-medium text-soft-text">Project Data</p>
            <p>
              Siftrio stores information you create or upload within the
              application, including workspace details, project documentation,
              meeting notes, action items, and AI-generated summaries. This data
              is created by you and stored to power the features of the
              application.
            </p>
            <p className="font-medium text-soft-text">Usage Data</p>
            <p>
              We collect aggregated and anonymized product usage information,
              such as feature adoption and application performance metrics, to
              improve the reliability, security, and usability of Siftrio. This
              information does not include Google user data obtained through
              Google APIs.
            </p>
          </Section>

          {/* 03 How We Use Information */}
          <Section
            id="how-we-use-information"
            number="03"
            title="How We Use Information"
          >
            <p>We use the information we collect to:</p>
            <ul>
              <li>Provide, operate, and maintain the Siftrio platform</li>
              <li>Authenticate users and manage account access</li>
              <li>
                Power AI-generated summaries, insights, and assistant features
              </li>
              <li>
                Improve and optimize the application based on aggregated or
                anonymized usage patterns
              </li>
              <li>Communicate with you about updates, features, or support</li>
              <li>Ensure the security and integrity of our Services</li>
            </ul>
            <p>
              We do not use your data for advertising, profiling, or selling to
              third parties. Google user data obtained through Google APIs is
              not used for analytics, product improvement, advertising,
              profiling, or any purpose beyond providing the features you have
              explicitly requested.
            </p>
          </Section>

          {/* 04 Legal Basis for Processing */}
          <Section
            id="legal-basis"
            number="04"
            title="Legal Basis for Processing"
          >
            <p>
              We process your personal data under the following legal bases as
              defined by the General Data Protection Regulation (GDPR):
            </p>
            <ul>
              <li>
                <strong>Contractual necessity</strong> — Processing is necessary
                to provide the Services you have requested, including account
                management, project management, and AI-powered features
              </li>
              <li>
                <strong>Legitimate interests</strong> — Processing is necessary
                for our legitimate interest in securing the Services and
                preventing fraud
              </li>
              <li>
                <strong>User consent</strong> — Where you have given explicit
                consent, such as connecting Google Calendar or third-party
                integrations like Jira
              </li>
            </ul>
          </Section>

          {/* 05 Google Account Data */}
          <Section
            id="google-account-data"
            number="05"
            title="Google Account Data"
          >
            <p>
              Siftrio uses Google OAuth for authentication and may access
              certain Google account data to provide specific features.
            </p>
            <p className="font-medium text-soft-text">
              Google OAuth Scopes Requested
            </p>
            <p>Siftrio requests the following Google OAuth scopes:</p>
            <ul>
              <li>
                <strong>openid</strong> — Authenticates your identity through
                Google Sign-In
              </li>
              <li>
                <strong>email</strong> — Accesses your email address to identify
                your account
              </li>
              <li>
                <strong>profile</strong> — Accesses your name and profile
                picture for display within the application
              </li>
              <li>
                <strong>calendar.events</strong> — Reads and creates calendar
                events on your primary calendar to manage meeting scheduling and
                generate Google Meet links
              </li>
            </ul>
            <p className="font-medium text-soft-text">
              Google Account Information Accessed
            </p>
            <p>
              When you sign in with Google, we receive your name, email address,
              and profile picture. This is used solely for authentication and
              account identification.
            </p>
            <p className="font-medium text-soft-text">Google Calendar Data</p>
            <p>
              If you choose to connect Google Calendar, Siftrio accesses your
              primary calendar to read existing events and create new calendar
              events on your behalf, including events with Google Meet
              conference links. Siftrio requests read and write access to
              calendar events to enable meeting scheduling and synchronization
              features within the application.
            </p>
            <p className="font-medium text-soft-text">
              How Google Data Is Used
            </p>
            <ul>
              <li>
                Google account information is used only for authentication
              </li>
              <li>
                Google Calendar data is used only to read, create, and
                synchronize calendar events within Siftrio
              </li>
              <li>
                Google Workspace APIs are only used to provide features you have
                explicitly requested
              </li>
              <li>
                Your Google data is never used for advertising or marketing
                purposes
              </li>
              <li>
                Siftrio never sells your Google user data to any third party
              </li>
              <li>
                Your Google data is never used for profiling or to build
                advertising profiles
              </li>
              <li>
                Your Google data is never used to train, fine-tune, or improve
                generalized AI or machine learning models
              </li>
              <li>
                Siftrio&apos;s use and transfer of information received from
                Google APIs adheres to the{" "}
                <a
                  href="https://developers.google.com/terms/api-services-user-data-policy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
                >
                  Google API Services User Data Policy
                </a>
                , including the Limited Use requirements. Google user data is
                accessed and processed only to provide or improve user-facing
                features that you explicitly request
              </li>
            </ul>
            <p className="font-medium text-soft-text">
              Google API Services User Data Policy Compliance
            </p>
            <p>
              Siftrio&apos;s use of Google user data is subject to the Google
              API Services User Data Policy. Specifically:
            </p>
            <ul>
              <li>
                Google user data is used solely to provide the features
                explicitly requested by the user
              </li>
              <li>
                Google user data is never used for advertising, marketing,
                profiling, or sold to third parties
              </li>
              <li>
                Google user data is never used to train, fine-tune, or improve
                generalized AI or machine learning models
              </li>
              <li>
                Google user data is processed only for the functionality
                requested by the user
              </li>
              <li>
                Siftrio&apos;s use and transfer of information received from
                Google APIs adheres to the Google API Services User Data Policy,
                including the Limited Use requirements. Google user data is
                accessed and processed only to provide or improve user-facing
                features that you explicitly request
              </li>
            </ul>
            <p className="font-medium text-soft-text">
              AI and Machine Learning
            </p>
            <p>
              Siftrio uses artificial intelligence to generate summaries,
              insights, and assistant features within the application. Google
              Workspace API data is processed only to provide the requested
              functionality. Google user data obtained through Google OAuth and
              Google Workspace APIs is never used to train, fine-tune, develop,
              or improve generalized artificial intelligence or machine learning
              models. Google data is never used outside the scope of the
              user&apos;s requested feature.
            </p>
            <p className="font-medium text-soft-text">Revoking Access</p>
            <p>
              You can revoke Siftrio&apos;s access to your Google account at any
              time by visiting{" "}
              <a
                href="https://myaccount.google.com/permissions"
                target="_blank"
                rel="noopener noreferrer"
                className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
              >
                Google Account Permissions
              </a>
              . Revoking access will disable Google-related features but will
              not delete your existing Siftrio account or data. To request
              deletion of your Siftrio account and associated data, contact{" "}
              <span className="text-foreground">appsbysneha@gmail.com</span>.
            </p>
          </Section>

          {/* 06 Third-Party Integrations */}
          <Section
            id="third-party-integrations"
            number="06"
            title="Third-Party Integrations"
          >
            <p>
              Siftrio may integrate with third-party services such as Jira to
              provide enhanced features. When you connect a third-party service,
              we only access the data necessary to provide the feature you have
              requested.
            </p>
            <p>
              Third-party integrations are subject to their own privacy
              policies. We encourage you to review the privacy policies of any
              third-party service you connect to Siftrio. We are not responsible
              for the practices of third-party services.
            </p>
          </Section>

          {/* 07 Data Storage */}
          <Section id="data-storage" number="07" title="Data Storage">
            <p>
              Your data is stored on secure cloud infrastructure. We implement
              industry-standard security measures to protect your information,
              including encryption in transit and at rest.
            </p>
            <p>
              We retain your data for as long as your account is active or as
              needed to provide the Services. If you request account deletion by
              contacting appsbysneha@gmail.com, we will remove your personal
              data within thirty (30) days, except where required by law. Google
              user data obtained through OAuth is deleted within thirty (30)
              days of account deletion.
            </p>
          </Section>

          {/* 08 Data Sharing */}
          <Section id="data-sharing" number="08" title="Data Sharing">
            <p>
              Siftrio does not sell, trade, or rent your personal information to
              third parties. We may share information only in the following
              circumstances:
            </p>
            <ul>
              <li>With your explicit consent</li>
              <li>
                To comply with legal obligations or respond to lawful requests
              </li>
              <li>
                To protect the rights, property, or safety of Siftrio, our
                users, or the public
              </li>
              <li>
                With service providers who assist in operating our platform,
                subject to strict data protection obligations
              </li>
            </ul>
          </Section>

          {/* 09 Data Security */}
          <Section id="data-security" number="09" title="Data Security">
            <p>
              We take the security of your data seriously. We implement
              appropriate technical and organizational measures to protect your
              personal information against unauthorized access, alteration,
              disclosure, or destruction.
            </p>
            <p>
              These measures include encrypted communications (TLS), secure
              authentication via OAuth, access controls, and regular security
              reviews. While we strive to protect your data, no method of
              transmission or storage is 100% secure.
            </p>
          </Section>

          {/* 10 Cookies and Session Management */}
          <Section
            id="cookies-and-tracking"
            number="10"
            title="Cookies and Session Management"
          >
            <p>
              Siftrio uses cookies and similar session technologies to maintain
              your session, authenticate your account, and ensure security.
              These technologies are strictly necessary for the operation of the
              Services and cannot be disabled.
            </p>
            <p>
              We do not use advertising cookies, cross-site tracking cookies, or
              any analytics technologies that track users across websites.
            </p>
          </Section>

          {/* 11 Your Rights */}
          <Section id="your-rights" number="11" title="Your Rights">
            <p>You have the right to:</p>
            <ul>
              <li>Access the personal data we hold about you</li>
              <li>Request correction of inaccurate data</li>
              <li>Request deletion of your personal data</li>
              <li>Export your data in a portable format</li>
              <li>Object to or restrict certain processing of your data</li>
            </ul>
            <p>
              To exercise any of these rights, please contact us at{" "}
              <span className="text-foreground">appsbysneha@gmail.com</span>.
            </p>
          </Section>

          {/* 12 Children's Privacy */}
          <Section
            id="childrens-privacy"
            number="12"
            title="Children's Privacy"
          >
            <p>
              Siftrio is not intended for use by individuals under the age of
              16. We do not knowingly collect personal information from
              children. If we become aware that we have collected data from a
              child, we will take steps to delete that information promptly.
            </p>
          </Section>

          {/* 13 Changes to this Policy */}
          <Section
            id="changes-to-this-policy"
            number="13"
            title="Changes to this Policy"
          >
            <p>
              We may update this Privacy Policy from time to time. When we make
              material changes, we will notify you by updating the &quot;Last
              Updated&quot; date at the top of this page. We encourage you to
              review this policy periodically.
            </p>
          </Section>

          {/* 14 Contact Us */}
          <Section id="contact-us" number="14" title="Contact Us">
            <p>
              If you have any questions about this Privacy Policy or our data
              practices, please contact us:
            </p>
            <div className="mt-6 space-y-3">
              <div>
                <span className="text-[13px] text-subtle-text">Email</span>
                <p className="text-foreground">appsbysneha@gmail.com</p>
              </div>
              <div>
                <span className="text-[13px] text-subtle-text">Website</span>
                <p className="text-foreground">siftrio.tech</p>
              </div>
            </div>
          </Section>
        </div>

        {/* ── Footer ── */}
        <footer className="border-t border-border py-10">
          <div className="flex flex-col items-center gap-4 text-[13px] text-disabled-text">
            <div className="flex items-center gap-4">
              <Link
                href="/privacy"
                className="transition-colors hover:text-soft-text"
              >
                Privacy Policy
              </Link>
              <span>·</span>
              <Link
                href="/terms"
                className="transition-colors hover:text-soft-text"
              >
                Terms &amp; Conditions
              </Link>
            </div>
            <p className="text-faint-text">&copy; 2026 Siftrio</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

function Section({
  id,
  number,
  title,
  children,
}: {
  id: string;
  number: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 pb-20">
      <div className="mb-6">
        <span className="block text-[13px] font-medium text-faint-text">
          {number}
        </span>
        <h2 className="mt-1 text-[30px] font-semibold leading-tight tracking-tight text-foreground">
          {title}
        </h2>
      </div>
      <div className="space-y-6 text-[17px] leading-[1.8] text-disabled-text [&_li]:pl-1 [&_li]:marker:text-faint-text [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-5">
        {children}
      </div>
    </section>
  );
}
