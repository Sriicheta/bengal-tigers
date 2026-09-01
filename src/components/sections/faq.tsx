import * as React from "react";

import { SectionTag } from "@/components/ui/section-tag";
import { AccordionItem } from "@/components/ui/accordion-item";
import { FAQ_ITEMS } from "@/data/site-data";

export function Faq() {
  const [openFaq, setOpenFaq] = React.useState<number | null>(0);

  return (
    <section id="ccl" className="border-t border-line bg-navy py-24">
      <div className="mx-auto max-w-4xl px-5 md:px-8">
        <SectionTag>CCL &amp; Wildcards</SectionTag>
        <h2 className="mt-4 font-serif text-3xl font-semibold text-white sm:text-4xl">
          Questions, answered.
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
      </div>
    </section>
  );
}

export default Faq;
