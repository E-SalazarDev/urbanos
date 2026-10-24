import { StyleSheet, View } from 'react-native';

import { Presionable } from '../Presionable';
import { COLORES_CAMARA } from './colores';
import type { ModoCaptura } from './SelectorModo';

type Props = {
  modo: ModoCaptura;
  onPress?: () => void;
};


export function BotonDisparo({ modo, onPress }: Props) {
  return (
    <Presionable
      onPress={onPress}
      haptico
      accessibilityLabel={modo === 'foto' ? 'Tomar foto' : 'Grabar video'}
      estilo={estilos.anillo}
    >
      <View style={[estilos.centro, modo === 'video' && estilos.centroVideo]} />
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
  centroVideo: { backgroundColor: COLORES_CAMARA.grabando },
});