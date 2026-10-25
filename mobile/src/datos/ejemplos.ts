import type { TipoDano } from '../constants/danos';

export type DeteccionEjemplo = {
  id: string;
  tipo: TipoDano;
  confianza: number;
  caja: { x: number; y: number; ancho: number; alto: number };
};


export const DETECCIONES_EJEMPLO: DeteccionEjemplo[] = [
  { id: 'd1', tipo: 'D40', confianza: 0.94, caja: { x: 10, y: 48, ancho: 32, alto: 30 } },
  { id: 'd2', tipo: 'D20', confianza: 0.81, caja: { x: 52, y: 42, ancho: 34, alto: 30 } },
  { id: 'd3', tipo: 'D00', confianza: 0.67, caja: { x: 28, y: 18, ancho: 44, alto: 12 } },
];