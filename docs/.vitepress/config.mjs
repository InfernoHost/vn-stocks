import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'GSC Stock Exchange',
  description: 'Player guide for the Gearfall Stock Exchange trading bot',
  
  themeConfig: {
    logo: '/logo.png',
    
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Get Started', link: '/getting-started' },
      { text: 'Trading', link: '/trading' },
      { text: 'Advanced', link: '/advanced' },
      { text: 'GitHub', link: 'https://github.com/InfernoHost/vn-stocks' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'What is GSC?', link: '/' },
          { text: 'Getting Started', link: '/getting-started' }
        ]
      },
      {
        text: 'Trading',
        items: [
          { text: 'Trading Guide', link: '/trading' },
          { text: 'Strategies', link: '/trading#basic-trading-strategies' }
        ]
      },
      {
        text: 'Advanced',
        items: [
          { text: 'Limit Orders', link: '/advanced#limit-orders' },
          { text: 'Price Alerts', link: '/advanced#price-alerts' },
          { text: 'Watchlist', link: '/advanced#watchlist' },
          { text: 'Achievements', link: '/advanced#achievements-system' }
        ]
      },
      {
        text: 'Reference',
        items: [
          { text: 'All Commands', link: '/commands' },
          { text: 'FAQ', link: '/faq' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/InfernoHost/vn-stocks' }
    ],

    footer: {
      message: 'MIT Licensed',
      copyright: 'Copyright © 2026 InfernoHost'
    },

    search: {
      provider: 'local'
    }
  }
})
