import { Ionicons } from '@expo/vector-icons';
import { StyleSheet } from 'react-native';

import type { NombreIcono } from '../constants/danos';
import { espacio, radio, useTema } from '../theme';
import { Presionable } from './Presionable';
import { Texto } from './Texto';

type Props = {
  texto: string;
  onPress?: () => void;
  icono?: NombreIcono;
  variante?: 'primario' | 'secundario';
  deshabilitado?: boolean;
};

export function Boton({ texto, onPress, icono, variante = 'primario', deshabilitado }: Props) {
  const { paleta } = useTema();
  const fondo = variante === 'primario' ? paleta.primario : paleta.primarioSuave;
  const tinta = variante === 'primario' ? paleta.sobrePrimario : paleta.primario;

  return (
    <Presionable
      onPress={onPress}
      disabled={deshabilitado}
      haptico
      accessibilityLabel={texto}
      estilo={[estilos.base, { backgroundColor: fondo, opacity: deshabilitado ? 0.5 : 1 }]}
    >
      {icono ? <Ionicons name={icono} size={22} color={tinta} /> : null}
      <Texto variante="cuerpoFuerte" color={tinta}>
        {texto}
      </Texto>
    </Presionable>
  );
}

const estilos = StyleSheet.create({
  base: {
    minHeight: 52, 
    borderRadius: radio.lg,
    paddingHorizontal: espacio.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: espacio.sm,
  },
});
