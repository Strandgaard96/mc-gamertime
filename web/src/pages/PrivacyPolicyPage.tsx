import { ChevronLeft, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDate } from "../lib/utils";

const LAST_UPDATED = "2026-06-09";

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-2xl mx-auto p-4 md:p-6 space-y-8">
      <div>
        <Link
          to="/"
          className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 w-fit mb-4"
        >
          <ChevronLeft size={16} /> Home
        </Link>
        <h1 className="text-2xl font-display font-bold flex items-center gap-2">
          <ShieldCheck size={24} className="text-primary" />
          Privacy Policy
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Last updated {formatDate(LAST_UPDATED)}
        </p>
      </div>

      <div className="prose prose-sm prose-invert max-w-none">
        <p>
          This site is a private board game night tracker for a small group of friends. It is not a
          commercial product, and we do not sell, rent, or share your data with advertisers. This
          page explains what information the site stores and why.
        </p>

        <h2>What we collect</h2>
        <p>Accounts on this site are created by an admin, not via public sign-up. We store:</p>
        <ul>
          <li>Your username, display name, and a hashed (never plaintext) password</li>
          <li>Your role (admin or readonly), used to control access to features</li>
          <li>An optional profile avatar image, if you upload one</li>
          <li>Game session data you or other members log: results, scores, and dates</li>
          <li>Any blog posts or recommendations you author</li>
        </ul>

        <h2>Legal basis for processing</h2>
        <p>We process personal data on the following legal bases under GDPR Art. 6:</p>
        <ul>
          <li>
            <strong>Contract performance (Art. 6(1)(b)):</strong> Your username, hashed password,
            and role — necessary to provide the service; without them you cannot sign in.
          </li>
          <li>
            <strong>Legitimate interest (Art. 6(1)(f)):</strong> Game session logs, scores, dates,
            profile avatar, blog posts, and recommendations — these are the core purpose of the site
            and the reason accounts exist.
          </li>
        </ul>

        <h2>Cookies</h2>
        <p>
          The site sets a single cookie, <code>token</code>, containing a signed session token. It
          is used only to keep you signed in — never for tracking or advertising — and is marked{" "}
          <code>HttpOnly</code>, <code>Secure</code>, and <code>SameSite=Strict</code> so it cannot
          be read by scripts or sent to other sites. It expires after 7 days.
        </p>

        <h2>Third-party services</h2>
        <ul>
          <li>
            <strong>BoardGameGeek (BGG):</strong> game search and details are fetched from BGG's
            public API. Only game titles/IDs are sent — never your personal data.
          </li>
          <li>
            <strong>Hosting:</strong> the site and its data are hosted on Amazon Web Services
            (CloudFront, S3, Lambda, DynamoDB) in the EU (Ireland), with DNS routed through
            Cloudflare. Fonts are self-hosted — no external font CDN requests. We don't use any
            analytics or tracking scripts.
          </li>
        </ul>

        <h2>Data retention &amp; deletion</h2>
        <p>
          We keep your data for as long as your account exists. If you'd like your account, avatar,
          or logged data corrected or removed, contact the site admin (see below) and we'll take
          care of it.
        </p>

        <h2>Your rights</h2>
        <p>Under GDPR Arts. 15–21 you have the right to:</p>
        <ul>
          <li>
            <strong>Access (Art. 15):</strong> request a copy of your personal data.
          </li>
          <li>
            <strong>Rectification (Art. 16):</strong> request correction of inaccurate data.
          </li>
          <li>
            <strong>Erasure (Art. 17):</strong> request deletion of your account and associated
            data.
          </li>
          <li>
            <strong>Restriction (Art. 18):</strong> request that processing be restricted while a
            dispute is resolved.
          </li>
          <li>
            <strong>Portability (Art. 20):</strong> request your data in a machine-readable format.
          </li>
          <li>
            <strong>Object (Art. 21):</strong> object to processing based on legitimate interest.
          </li>
        </ul>
        <p>
          You may also lodge a complaint with{" "}
          <a
            href="https://www.datatilsynet.dk"
            className="text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Datatilsynet
          </a>{" "}
          (Carl Jacobsens Vej 35, 2500 Valby, Denmark), the Danish supervisory authority. To
          exercise any of the above rights, contact the site admin (see below).
        </p>

        <h2>Changes to this policy</h2>
        <p>
          If this policy changes, we'll update the "last updated" date above. Since this is a small
          site for a known group, we'll also let you know directly.
        </p>

        <h2>Contact</h2>
        <p>
          To exercise your data rights or ask questions about this policy, reach out via{" "}
          <a
            href="https://links.strandgaard.dev"
            className="text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            strandgaard.dev
          </a>
          .
        </p>
      </div>
    </div>
  );
}
