import {
  Trophy,
  Swords,
  Users,
  Globe2,
  Flame,
  Target,
  ShieldCheck,
} from "lucide-react";

import type { Player } from "@/components/ui/player-carousel";

import heroBatsman from "@/assets/hero-batsman.png";
import bengalTigersLogo from "@/assets/bengal-tigers-logo.svg";
import ownerBoneyKapoor from "@/assets/owner-boney-kapoor.png";
import ownerArjunKapoor from "@/assets/owner-arjun-kapoor.png";
import ownerBinaShah from "@/assets/owner-bina-shah-framed.png";

import playerUdayPratapSingh from "@/assets/player-01-uday-pratap-singh.png";
import playerAnirbanChakraborty from "@/assets/player-02-anirban-chakraborty.png";
import playerBonnySengupta from "@/assets/player-03-bonny-sengupta.png";
import playerSauravDas from "@/assets/player-04-saurav-das.png";
import playerJishuSengupta from "@/assets/player-05-jishu-sengupta.png";
import playerAnandaChoudhuri from "@/assets/player-06-ananda-choudhuri.png";
import playerRatnadeepGhosh from "@/assets/player-07-ratnadeep-ghosh.png";
import playerJoeyDebRoy from "@/assets/player-08-joey-deb-roy.png";
import playerRahulMazumdar from "@/assets/player-09-rahul-mazumdar.png";
import playerJoyMukherjee from "@/assets/player-10-joy-mukherjee.png";
import playerJammyBanerjee from "@/assets/player-11-jammy-banerjee.png";
import headCoachSaradinduMukherjee from "@/assets/headcoach-saradindu-mukherjee.jpeg";

export { bengalTigersLogo, heroBatsman };

export const HEADLINE_WORDS = ["Strength", "Passion", "Glory", "Heritage"];

export const SEASON_RECORD = [
  "Joined 2012",
  "2024 Champions",
  "2026 Runners-up",
];

export const CONTACT = {
  location: "Kolkata, West Bengal",
  phone: "+91 91477 26162",
  instagramUrl: "https://www.instagram.com/bengaltigers.ccl",
  instagramHandle: "@bengaltigers.ccl",
  facebookUrl: "https://www.facebook.com/share/1HRtoBdhDM/?mibextid=wwXIfr",
  linkedinUrl: "https://www.linkedin.com/company/bengal-tigers-ccl/",
};

export const OWNERS = [
  {
    name: "Boney Kapoor",
    image: ownerBoneyKapoor,
    imagePosition: "50% 22%",
    imageScale: 1.18,
    note: "Chairman · Sets the ambition for the franchise.",
  },
  {
    name: "Arjun Kapoor",
    image: ownerArjunKapoor,
    imagePosition: "50% 16%",
    imageScale: 1.12,
    note: "Ambassador · The energy behind every boundary rope.",
  },
  {
    name: "Bina Shah",
    image: ownerBinaShah,
    imagePosition: "50% 25%",
    imageScale: 1,
    note: "Operations · Squad logistics and matchday command.",
  },
];

export const PILLARS = [
  {
    icon: Flame,
    title: "PASSION",
    copy: "Every over is played like it's the final — a squad that trains hard and backs itself without exception.",
  },
  {
    icon: Target,
    title: "FOCUS",
    copy: "Disciplined preparation off the field translates into composure under pressure when it matters most.",
  },
  {
    icon: ShieldCheck,
    title: "LEGACY",
    copy: "Carrying Bengal's cricketing pride forward, season after season, for the fans who never stop showing up.",
  },
];

export const STATS = [
  { icon: Swords, label: "Matches Played", value: "125+" },
  { icon: Trophy, label: "Wins", value: "75+" },
  { icon: Users, label: "Championships", value: "1" },
  { icon: Globe2, label: "Fans Worldwide", value: "1M+" },
];

export const HEAD_COACH: Player = {
  id: "coach-01",
  name: "Saradindu Mukherjee",
  jerseyNumber: 0,
  image: headCoachSaradinduMukherjee,
  role: "Head Coach",
  isCoach: true,
};

export const PLAYERS: Player[] = [
  { id: "player-5", name: "Jishu Sengupta", jerseyNumber: 1, image: playerJishuSengupta, role: "Captain" },
  { id: "player-3", name: "Bonny Sengupta", jerseyNumber: 3, image: playerBonnySengupta, role: "Batter", battingStyle: "RHB" },
  { id: "player-4", name: "Saurav Das", jerseyNumber: 2, image: playerSauravDas, role: "Wicket-Keeper" },
  { id: "player-10", name: "Joy Mukherjee", jerseyNumber: 10, image: playerJoyMukherjee, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAO" },
  { id: "player-1", name: "Uday Pratap Singh", jerseyNumber: 4, image: playerUdayPratapSingh, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAM" },
  { id: "player-9", name: "Rahul Mazumdar", jerseyNumber: 9, image: playerRahulMazumdar, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAM" },
  { id: "player-11", name: "Jammy Banerjee", jerseyNumber: 11, image: playerJammyBanerjee, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAM" },
  { id: "player-8", name: "Joey Deb Roy", jerseyNumber: 8, image: playerJoeyDebRoy, role: "Batter", battingStyle: "RHB" },
  { id: "player-6", name: "Ananda Choudhuri", jerseyNumber: 6, image: playerAnandaChoudhuri, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAO" },
  { id: "player-7", name: "Ratnadeep Ghosh", jerseyNumber: 7, image: playerRatnadeepGhosh, role: "All-Rounder", battingStyle: "RHB", bowlingStyle: "RAL" },
  { id: "player-2", name: "Anirban Chakraborty", jerseyNumber: 5, image: playerAnirbanChakraborty, role: "All-Rounder", battingStyle: "LHB", bowlingStyle: "RAM" },
];

export const ROSTER: Player[] = PLAYERS;

export const FAQ_ITEMS = [
  {
    q: "What is the CCL Wildcard?",
    a: "For the first time, passionate cricketers beyond the world of cinema have the opportunity to compete for a place within a CCL team and potentially share the field with some of India's biggest film stars. Introduced for CCL Season 13 in 2027, the CCL Wildcard provides a structured pathway for talented cricket enthusiasts to register, attend trials, showcase their ability and compete for an opportunity to represent a CCL franchise.",
  },
  {
    q: "How can I represent Bengal Tigers?",
    a: "For aspiring cricketers in Bengal, the Wildcard offers the opportunity to chase something extraordinary: earning a place alongside the stars of Bengal Tigers. Show your skill. Prove your fitness. Compete with the best. If you have what it takes, you could find yourself wearing the Bengal Tigers jersey and stepping onto the CCL stage. The Tigers are looking for their next player.",
  },
  {
    q: "Are you ready? How do I get started?",
    a: "Register for the CCL Wildcard, prepare for the trials and give your cricketing journey the opportunity it deserves. Your cricket. Your chance. Your Bengal Tigers moment.",
  },
];

export const NAV_FOOTER_LINKS = [
  { label: "Home", href: "#top" },
  { label: "Team", href: "#roster" },
  { label: "Owners", href: "#owners" },
  { label: "Matches", href: "#stats" },
  { label: "News", href: "#ccl" },
];
