import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import { espacio, radio } from '../../theme';
import { Texto } from '../Texto';
import { COLORES_CAMARA } from './colores';

type Props = { estado?: 'listo' | 'buscando' };


export function EstadoGps({ estado = 'listo' }: Props) {
  const listo = estado === 'listo';
  const color = listo ? COLORES_CAMARA.exito : COLORES_CAMARA.alerta;

  return (
    <View style={estilos.chip} accessible accessibilityLabel={listo ? 'GPS listo' : 'Buscando GPS'}>
      <Ionicons name={listo ? 'location' : 'locate-outline'} size={16} color={color} />
      <Texto variante="micro" color={COLORES_CAMARA.blanco}>
        {listo ? 'GPS listo' : 'Buscando GPS…'}
      </Texto>
    </View>
  );
}

const estilos = StyleSheet.create({
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: espacio.xs + 2,
    paddingHorizontal: espacio.sm + 4,
    paddingVertical: espacio.sm,
    borderRadius: radio.pildora,
    backgroundColor: COLORES_CAMARA.vidrio,
  },
});