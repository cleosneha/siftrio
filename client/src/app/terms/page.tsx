"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";

const EASE = [0.25, 0.1, 0.25, 1] as const;

const SECTIONS = [
  { id: "introduction", label: "Introduction" },
  { id: "eligibility", label: "Eligibility" },
  { id: "account-registration", label: "Account Registration" },
  { id: "ai-features", label: "AI Features and Summaries" },
  { id: "google-calendar", label: "Google Calendar Integration" },
  { id: "mcp-protocol", label: "MCP Protocol Integration" },
  { id: "user-content", label: "User Content and Data" },
  { id: "user-responsibilities", label: "User Responsibilities" },
  { id: "intellectual-property", label: "Intellectual Property" },
  { id: "subscriptions-and-billing", label: "Subscriptions and Billing" },
  { id: "termination", label: "Termination" },
  { id: "disclaimers", label: "Disclaimers" },
  { id: "limitation-of-liability", label: "Limitation of Liability" },
  { id: "indemnification", label: "Indemnification" },
  { id: "contact-information", label: "Contact Information" },
];

export default function TermsAndConditions() {
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
            Terms &amp; Conditions
          </h1>

          <div className="mt-6 flex gap-10 text-[13px] text-disabled-text">
            <div>
              <span className="block text-subtle-text">Effective Date</span>
              July 17, 2026
            </div>
            <div>
              <span className="block text-subtle-text">Last Updated</span>
              July 17, 2026
            </div>
          </div>

          <p className="mt-10 max-w-[640px] text-[17px] leading-[1.8] text-disabled-text">
            These Terms &amp; Conditions govern your access to and use of
            Siftrio. By using our services, you agree to these terms.
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
              Siftrio (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;)
              provides an AI-native platform for project memory and management.
              These Terms &amp; Conditions (&quot;Terms&quot;) govern your
              access to and use of the Siftrio website, applications, APIs, and
              related services (collectively, the &quot;Services&quot;).
            </p>
            <p>
              Please read these Terms carefully before using the Services. By
              accessing or using Siftrio, you agree to be bound by these Terms.
              If you do not agree, you may not use the Services.
            </p>
          </Section>

          {/* 02 Acceptance of Terms */}
          <Section
            id="acceptance-of-terms"
            number="02"
            title="Acceptance of Terms"
          >
            <p>
              By creating an account, accessing, or using the Services, you
              acknowledge that you have read, understood, and agree to be bound
              by these Terms and our{" "}
              <Link
                href="/privacy"
                className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
              >
                Privacy Policy
              </Link>
              . If you are using the Services on behalf of an organization, you
              represent and warrant that you have the authority to bind that
              organization to these Terms.
            </p>
          </Section>

          {/* 03 Eligibility */}
          <Section id="eligibility" number="03" title="Eligibility">
            <p>
              The Services are intended for use by individuals who are at least
              16 years of age. By using Siftrio, you represent and warrant that
              you meet this age requirement and have the legal capacity to enter
              into a binding agreement.
            </p>
          </Section>

          {/* 04 User Accounts */}
          <Section id="user-accounts" number="04" title="User Accounts">
            <p>
              To use certain features of the Services, you must create an
              account. When you create an account, you agree to:
            </p>
            <ul>
              <li>Provide accurate, current, and complete information</li>
              <li>
                Maintain the security of your password and account credentials
              </li>
              <li>
                Accept responsibility for all activities that occur under your
                account
              </li>
              <li>
                Notify us immediately of any unauthorized use of your account
              </li>
            </ul>
            <p>
              We reserve the right to suspend or terminate accounts that contain
              inaccurate information or that we reasonably believe are being
              used in violation of these Terms.
            </p>
          </Section>

          {/* 05 Use of the Service */}
          <Section
            id="use-of-the-service"
            number="05"
            title="Use of the Service"
          >
            <p>
              Subject to these Terms, we grant you a limited, non-exclusive,
              non-transferable, and revocable license to access and use the
              Services for your internal business or personal purposes.
            </p>
            <p>You agree not to:</p>
            <ul>
              <li>Use the Services for any unlawful purpose</li>
              <li>
                Attempt to gain unauthorized access to any part of the Services
              </li>
              <li>
                Interfere with or disrupt the integrity or performance of the
                Services
              </li>
              <li>
                Reverse engineer, decompile, or disassemble any aspect of the
                Services
              </li>
              <li>Use the Services to build a competing product or service</li>
              <li>Exceed any applicable usage limits or quotas</li>
            </ul>
          </Section>

          {/* 06 Google Integrations */}
          <Section
            id="google-integrations"
            number="06"
            title="Google Integrations"
          >
            <p>
              Siftrio integrates with Google services to provide enhanced
              functionality. By connecting your Google account, you agree to the
              following:
            </p>
            <p className="font-medium text-soft-text">Account Connection</p>
            <p>
              Users choose which Google account to connect to Siftrio. The
              connection is initiated and authorized entirely by the user
              through Google&apos;s standard OAuth flow. Siftrio does not access
              any Google data without explicit user authorization.
            </p>
            <p className="font-medium text-soft-text">Data Usage</p>
            <p>
              Google account data is accessed and processed only to provide the
              specific features you have requested. Google Workspace APIs are
              not used for advertising, marketing, or any purpose other than
              delivering the requested functionality.
            </p>
            <p className="font-medium text-soft-text">Revoking Access</p>
            <p>
              You may revoke Siftrio&apos;s access to your Google account at any
              time through your{" "}
              <a
                href="https://myaccount.google.com/permissions"
                target="_blank"
                rel="noopener noreferrer"
                className="text-foreground underline underline-offset-4 transition-colors hover:text-soft-text"
              >
                Google Account Permissions
              </a>{" "}
              settings. Revoking access will disable Google-related features
              within Siftrio but will not delete your Siftrio account or data.
              To request account deletion, contact{" "}
              <span className="text-foreground">siftriosupport@gmail.com</span>.
            </p>
            <p className="font-medium text-soft-text">Compliance</p>
            <p>
              Siftrio complies with Google&apos;s API Services User Data Policy,
              including the Limited Use requirements. User data obtained through
              Google APIs is not transferred to third parties, is not used for
              advertising, and is only used to provide the functionality
              requested by the user.
            </p>
          </Section>

          {/* 07 Third-Party Services */}
          <Section
            id="third-party-services"
            number="07"
            title="Third-Party Services"
          >
            <p>
              The Services may integrate with or contain links to third-party
              services, including but not limited to Jira. These third-party
              services are governed by their own terms and privacy policies.
            </p>
            <p>
              We are not responsible for the availability, accuracy, content,
              products, or services of any third-party service. Your use of
              third-party services is at your own risk and subject to the
              applicable third-party terms.
            </p>
          </Section>

          {/* 08 User Responsibilities */}
          <Section
            id="user-responsibilities"
            number="08"
            title="User Responsibilities"
          >
            <p>By using Siftrio, you agree to:</p>
            <ul>
              <li>Provide accurate and truthful account information</li>
              <li>Keep your account credentials secure and confidential</li>
              <li>Use the platform only for its intended purpose</li>
              <li>
                Not attempt to access, modify, or disrupt other users&apos; data
                or system infrastructure
              </li>
              <li>
                Comply with all applicable local, state, national, and
                international laws and regulations
              </li>
              <li>
                Promptly report any security vulnerabilities or misuse of the
                platform
              </li>
            </ul>
          </Section>

          {/* 09 Intellectual Property */}
          <Section
            id="intellectual-property"
            number="09"
            title="Intellectual Property"
          >
            <p className="font-medium text-soft-text">Siftrio Ownership</p>
            <p>
              The Services, including all software, design, branding, logos,
              documentation, and related intellectual property, are owned by
              Siftrio and protected by copyright, trademark, and other
              intellectual property laws. Nothing in these Terms grants you any
              right to use our trademarks, logos, or branding without prior
              written consent.
            </p>
            <p className="font-medium text-soft-text">Your Content</p>
            <p>
              You retain full ownership of all content you create, upload, or
              generate within the Services, including project data, meeting
              notes, documentation, and any other materials.
            </p>
            <p className="font-medium text-soft-text">License to Process</p>
            <p>
              By using the Services, you grant Siftrio a limited license to
              process your uploaded content solely for the purpose of providing
              the requested features, including AI-powered summaries, insights,
              and assistant functionality. This license terminates when you
              request deletion of your content or account.
            </p>
          </Section>

          {/* 10 Subscriptions and Billing */}
          <Section
            id="subscriptions-and-billing"
            number="10"
            title="Subscriptions and Billing"
          >
            <p>
              Siftrio may offer free and paid subscription tiers. The features,
              limitations, and pricing of each tier will be described at the
              time of purchase.
            </p>
            <p>
              Paid subscriptions are billed in advance on a recurring basis. All
              fees are non-refundable unless otherwise required by applicable
              law. We reserve the right to modify pricing with reasonable
              advance notice.
            </p>
            <p>
              <em>
                This section will be updated with specific billing terms when
                paid plans are introduced.
              </em>
            </p>
          </Section>

          {/* 11 Termination */}
          <Section id="termination" number="11" title="Termination">
            <p>
              You may request account termination at any time by contacting us
              at siftriosupport@gmail.com. Upon termination, your right to use
              the Services ceases immediately.
            </p>
            <p>
              We may suspend or terminate your access to the Services at our
              discretion, with or without cause, including but not limited to
              violations of these Terms. Upon termination, we will provide your
              data in a commonly used format upon request.
            </p>
            <p>
              Sections of these Terms that by their nature should survive
              termination will survive, including ownership provisions, warranty
              disclaimers, and limitations of liability.
            </p>
          </Section>

          {/* 12 Disclaimers */}
          <Section id="disclaimers" number="12" title="Disclaimers">
            <p>
              The Services are provided on an &quot;as is&quot; and &quot;as
              available&quot; basis without warranties of any kind, whether
              express, implied, or statutory.
            </p>
            <p>
              We do not warrant that the Services will be uninterrupted,
              error-free, secure, or free of viruses or other harmful
              components. We make no guarantees regarding the accuracy,
              reliability, or completeness of any content provided through the
              Services.
            </p>
            <p>
              AI-generated content, including summaries, insights, and
              recommendations, is produced by automated systems and may contain
              inaccuracies. You should review and verify AI-generated content
              before relying on it for business decisions or taking action based
              on it.
            </p>
          </Section>

          {/* 13 Limitation of Liability */}
          <Section
            id="limitation-of-liability"
            number="13"
            title="Limitation of Liability"
          >
            <p>
              To the maximum extent permitted by applicable law, Siftrio, its
              directors, employees, partners, agents, suppliers, and affiliates
              shall not be liable for any indirect, incidental, special,
              consequential, or punitive damages, including but not limited to
              loss of profits, data, business opportunities, or goodwill,
              arising out of or in connection with your use of the Services,
              regardless of the theory of liability.
            </p>
            <p>
              In no event shall our total aggregate liability exceed the greater
              of one hundred U.S. dollars (USD $100.00) or the amount you have
              paid to Siftrio in the twelve (12) months preceding the claim.
            </p>
          </Section>

          {/* 14 Changes to the Terms */}
          <Section
            id="changes-to-the-terms"
            number="14"
            title="Changes to the Terms"
          >
            <p>
              We reserve the right to modify these Terms at any time. When we
              make material changes, we will update the &quot;Last Updated&quot;
              date at the top of this page and provide notice through the
              Services or by other reasonable means.
            </p>
            <p>
              Your continued use of the Services after any changes to these
              Terms constitutes your acceptance of the updated Terms. If you do
              not agree to the modified Terms, you must stop using the Services.
            </p>
          </Section>

          {/* 15 Contact Information */}
          <Section
            id="contact-information"
            number="15"
            title="Contact Information"
          >
            <p>
              If you have any questions about these Terms &amp; Conditions,
              please contact us:
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
