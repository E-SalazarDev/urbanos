import { Platform, useColorScheme, type ViewStyle } from 'react-native';

export type Paleta = {
  fondo: string;
  superficie: string;
  superficieAlta: string; 
  texto: string;
  textoSuave: string;
  borde: string;
  primario: string;
  sobrePrimario: string; 
  primarioSuave: string;
  exito: string;
  alerta: string;
  peligro: string;
};

export const colores: { claro: Paleta; oscuro: Paleta } = {
  claro: {
    fondo: '#F6F7F9',
    superficie: '#FFFFFF',
    superficieAlta: '#E9ECF1',
    texto: '#101828',
    textoSuave: '#667085',
    borde: '#E4E7EC',
    primario: '#2563EB',
    sobrePrimario: '#FFFFFF',
    primarioSuave: '#DBEAFE',
    exito: '#16A34A',
    alerta: '#D97706',
    peligro: '#DC2626',
  },
  oscuro: {
    fondo: '#0B0F14',
    superficie: '#151B23',
    superficieAlta: '#222B38',
    texto: '#F2F4F7',
    textoSuave: '#98A2B3',
    borde: '#263040',
    primario: '#5B8DEF',
    sobrePrimario: '#0B0F14',
    primarioSuave: '#1E2A44',
    exito: '#34D399',
    alerta: '#FBBF24',
    peligro: '#F87171',
  },
};


export const espacio = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48 } as const;


export const radio = { sm: 8, md: 12, lg: 16, xl: 24, pildora: 999 } as const;


export const tipografia = {
  titulo: { fontSize: 30, lineHeight: 36, fontWeight: '700' },
  subtitulo: { fontSize: 20, lineHeight: 26, fontWeight: '600' },
  cuerpo: { fontSize: 16, lineHeight: 24, fontWeight: '400' },
  cuerpoFuerte: { fontSize: 16, lineHeight: 24, fontWeight: '600' },
  pequeno: { fontSize: 14, lineHeight: 20, fontWeight: '400' },
  micro: { fontSize: 12, lineHeight: 16, fontWeight: '500' },
} as const;

export type Variante = keyof typeof tipografia;


export function sombra(nivel: 1 | 2 | 3): ViewStyle {
  const alto = { 1: 2, 2: 6, 3: 12 } as const;
  return (
    Platform.select<ViewStyle>({
      ios: {
        shadowColor: '#000',
        shadowOpacity: 0.06 + nivel * 0.02,
        shadowRadius: alto[nivel] * 1.5,
        shadowOffset: { width: 0, height: alto[nivel] / 2 },
      },
      default: { elevation: nivel * 2 + 1 },
    }) ?? {}
  );
}


export function useTema() {
  const oscuro = useColorScheme() === 'dark';
  return { oscuro, paleta: oscuro ? colores.oscuro : colores.claro };
}
