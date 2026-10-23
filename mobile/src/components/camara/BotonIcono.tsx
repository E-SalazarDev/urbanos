import { Ionicons } from '@expo/vector-icons';
import { StyleSheet } from 'react-native';

import type { NombreIcono } from '../../constants/danos';
import { Presionable } from '../Presionable';
import { COLORES_CAMARA } from './colores';

type Props = {
  icono: NombreIcono;
  etiqueta: string;
  onPress?: () => void;
  tamano?: number;
};


export function BotonIcono({ icono, etiqueta, onPress, tamano = 48 }: Props) {
  return (
    <Presionable
      onPress={onPress}
      haptico
      accessibilityLabel={etiqueta}
      estilo={[estilos.base, { width: tamano, height: tamano, borderRadius: tamano / 2 }]}
    >
      <Ionicons name={icono} size={tamano * 0.5} color={COLORES_CAMARA.blanco} />
    </Presionable>
  );
}

const estilos = StyleSheet.create({
  base: {
    backgroundColor: COLORES_CAMARA.vidrio,
    alignItems: 'center',
    justifyContent: 'center',
  },
});