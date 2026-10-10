import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import type { NombreIcono } from '../constants/danos';
import { espacio, radio, useTema } from '../theme';
import { Texto } from './Texto';

type Props = {
  texto: string;
  icono?: NombreIcono;
  color?: string; 
};


export function Insignia({ texto, icono, color }: Props) {
  const { paleta } = useTema();
  const tono = color ?? paleta.primario;

  return (
    <View style={[estilos.base, { backgroundColor: tono + '22' }]} accessible accessibilityLabel={texto}>
      {icono ? <Ionicons name={icono} size={14} color={tono} /> : null}
      <Texto variante="micro">{texto}</Texto>
    </View>
  );
}

const estilos = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: espacio.xs,
    paddingHorizontal: espacio.sm + 2,
    paddingVertical: espacio.xs + 2,
    borderRadius: radio.pildora,
  },
});
