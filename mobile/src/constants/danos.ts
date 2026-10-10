import type { Ionicons } from '@expo/vector-icons';

export type NombreIcono = keyof typeof Ionicons.glyphMap;

type Info = { nombre: string; icono: NombreIcono; color: string };

export const TIPOS_DANO = {
  D40: { nombre: 'Bache', icono: 'alert-circle', color: '#DC2626' },
  D20: { nombre: 'Piel de cocodrilo', icono: 'grid', color: '#D97706' },
  D00: { nombre: 'Grieta longitudinal', icono: 'swap-vertical', color: '#7C3AED' },
  D10: { nombre: 'Grieta transversal', icono: 'swap-horizontal', color: '#0891B2' },
} satisfies Record<string, Info>;

export const ESTADOS_TRAMO = {
  bueno: { nombre: 'Bueno', icono: 'checkmark-circle', color: '#16A34A' },
  regular: { nombre: 'Regular', icono: 'warning', color: '#D97706' },
  malo: { nombre: 'Malo', icono: 'close-circle', color: '#DC2626' },
} satisfies Record<string, Info>;
