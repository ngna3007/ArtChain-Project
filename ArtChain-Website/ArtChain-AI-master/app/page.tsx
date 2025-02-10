// app/page.tsx
'use client'
import Hero from '@/app/components/Hero'
import Features from '@/app/components/Features'
import ArtistSection from '@/app/components/ArtistSection'
import OnScrollSection from './components/on-scroll-tutorial'
import { artistCollections } from '@/app/lib/artistCollections'
import { Artist } from '@/app/lib/types'
import ContactForm from './components/drop-us-a-line'
import SliderPage from './components/ImageSlider'

export default function Home() {
  const handleViewGallery = (artist: { artist: Artist }) => {
    const artistData = artistCollections[artist.artist];
    if (artistData) {
      window.scrollTo(0, 0);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white">
      <Hero />
      <ArtistSection onViewGallery={handleViewGallery} />
      <SliderPage/>
      <OnScrollSection/>
      <Features />
      <ContactForm/>
    </main>
  )
}