import * as React from "react";
import { ExternalLink } from "lucide-react";

import { SectionTag } from "@/components/ui/section-tag";
import { AccordionItem } from "@/components/ui/accordion-item";
import { FAQ_ITEMS } from "@/data/site-data";

export function Faq() {
  const [openFaq, setOpenFaq] = React.useState<number | null>(0);

  return (
    <section id="ccl" className="border-t border-line bg-navy py-24">
      <div className="mx-auto max-w-4xl px-5 md:px-8">
        <SectionTag>CCL Wildcard</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          Your Chance. Your Cricket. Your Moment.
        </h2>

        <div className="mt-12">
          {FAQ_ITEMS.map((item, i) => (
            <AccordionItem
              key={item.q}
              q={item.q}
              a={item.a}
              open={openFaq === i}
              onToggle={() => setOpenFaq(openFaq === i ? null : i)}
            />
          ))}
        </div>

        <a
          href="https://ccl.in"
          target="_blank"
          rel="noreferrer"
          className="mt-10 inline-flex items-center gap-2 rounded-full bg-crimson px-7 py-3 text-sm font-semibold uppercase tracking-wide text-white transition-colors hover:bg-crimson-bright"
        >
          Register on ccl.in
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </section>
  );
}

export default Faq;
