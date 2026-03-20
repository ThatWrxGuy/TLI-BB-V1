import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
  colors: {
    brand: {
      50: '#FFF5E6',
      100: '#FFE0B3',
      200: '#FFCC80',
      300: '#FFB84D',
      400: '#FFA31A',
      500: '#F59E0B',
      600: '#D97706',
      700: '#B45309',
      800: '#92400E',
      700: '#78350F',
    },
    bee: {
      yellow: '#F59E0B',
      orange: '#EA580C',
      dark: '#1C1917',
      light: '#FAFAF9'
    }
  },
  fonts: {
    heading: 'Inter, sans-serif',
    body: 'Inter, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: '#FAFAF9',
        color: '#1C1917',
      }
    }
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '600',
        borderRadius: 'lg',
      },
      variants: {
        solid: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
          }
        },
        outline: {
          borderColor: 'brand.500',
          color: 'brand.500',
          _hover: {
            bg: 'brand.50',
          }
        }
      }
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: 'xl',
          boxShadow: 'sm',
        }
      }
    }
  }
})

export default theme
