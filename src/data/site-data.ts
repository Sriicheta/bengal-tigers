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
import ownerBoneyKapoor from "@/assets/owner-boney-kapoor-crop.jpg";
import ownerArjunKapoor from "@/assets/owner-arjun-kapoor-crop.jpg";
import ownerBinaShah from "@/assets/owner-bina-shah-crop.jpg";

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
  "2024 Champions",
  "2025 Semi-Finalists",
  "2026 Runners-up",
];

export const CONTACT = {
  location: "Kolkata, West Bengal",
  phone: "+91 91477 26162",
  instagramUrl: "https://www.instagram.com/bengaltigers.ccl",
  instagramHandle: "@bengaltigers.ccl",
  facebookUrl: "https://www.facebook.com/share/1HRtoBdhDM/?mibextid=wwXIfr",
};

export const OWNERS = [
  {
    name: "Bina Shah",
    image: ownerBinaShah,
    note: "Operations · Squad logistics and matchday command.",
  },
  {
    name: "Arjun Kapoor",
    image: ownerArjunKapoor,
    note: "Ambassador · The energy behind every boundary rope.",
  },
  {
    name: "Boney Kapoor",
    image: ownerBoneyKapoor,
    note: "Chairman · Sets the ambition for the franchise.",
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
  { icon: Users, label: "Championships", value: "3" },
  { icon: Globe2, label: "Fans Worldwide", value: "1M+" },
];

export const HEAD_COACH: Player = {
  id: "coach-01",
  name: "Saradindu Mukherjee",
  jerseyNumber: 0,
  image: headCoachSaradinduMukherjee,
  isCoach: true,
};

export const PLAYERS: Player[] = [
  { id: "player-1", name: "Uday Pratap Singh", jerseyNumber: 1, image: playerUdayPratapSingh },
  { id: "player-2", name: "Anirban Chakraborty", jerseyNumber: 2, image: playerAnirbanChakraborty },
  { id: "player-3", name: "Bonny Sengupta", jerseyNumber: 3, image: playerBonnySengupta },
  { id: "player-4", name: "Saurav Das", jerseyNumber: 4, image: playerSauravDas },
  { id: "player-5", name: "Jishu Sengupta", jerseyNumber: 5, image: playerJishuSengupta },
  { id: "player-6", name: "Ananda Choudhuri", jerseyNumber: 6, image: playerAnandaChoudhuri },
  { id: "player-7", name: "Ratnadeep Ghosh", jerseyNumber: 7, image: playerRatnadeepGhosh },
  { id: "player-8", name: "Joey Deb Roy", jerseyNumber: 8, image: playerJoeyDebRoy },
  { id: "player-9", name: "Rahul Mazumdar", jerseyNumber: 9, image: playerRahulMazumdar },
  { id: "player-10", name: "Joy Mukherjee", jerseyNumber: 10, image: playerJoyMukherjee },
  { id: "player-11", name: "Jammy Banerjee", jerseyNumber: 11, image: playerJammyBanerjee },
];

export const ROSTER: Player[] = PLAYERS;

export const FAQ_ITEMS = [
  {
    q: "What is CCL?",
    a: "The Celebrity Cricket League is a T20-format tournament where teams of film and television personalities compete on the pitch, blending genuine cricketing skill with the entertainment world's biggest names.",
  },
  {
    q: "Who can participate?",
    a: "Participation is open to actors, directors, and other recognised figures from regional film and entertainment industries, each drafted or retained by a franchise ahead of the season.",
  },
  {
    q: "How does Wildcard selection work?",
    a: "Wildcard slots let franchises bring in a late addition outside the standard draft, typically to fill a specific gap in the squad — an extra all-rounder, a specialist finisher, or a recognisable name for a particular fixture.",
  },
  {
    q: "What is the Team Selection Process?",
    a: "Squads are built through a mix of player retentions, an annual draft, and owner-nominated picks, with the final XI for each match chosen by the head coach and team management based on form and matchup.",
  },
];

export const NAV_FOOTER_LINKS = [
  { label: "Home", href: "#top" },
  { label: "Team", href: "#roster" },
  { label: "Owners", href: "#owners" },
  { label: "Matches", href: "#stats" },
  { label: "News", href: "#ccl" },
];
