import { StyleSheet, View } from 'react-native';

import { Presionable } from '../Presionable';
import { COLORES_CAMARA } from './colores';

/** Botón grande para tomar la foto. */
export function BotonDisparo({ onPress }: { onPress?: () => void }) {
  return (
    <Presionable onPress={onPress} haptico accessibilityLabel="Tomar foto" estilo={estilos.anillo}>
      <View style={estilos.centro} />
    </Presionable>
  );
}

const estilos = StyleSheet.create({
  anillo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    borderColor: COLORES_CAMARA.blanco,
    alignItems: 'center',
    justifyContent: 'center',
  },
  centro: {
    width: 62,
    height: 62,
    borderRadius: 31,
    backgroundColor: COLORES_CAMARA.blanco,
  },
});