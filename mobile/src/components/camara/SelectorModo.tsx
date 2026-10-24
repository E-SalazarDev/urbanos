import { StyleSheet, View } from 'react-native';

import { espacio, radio } from '../../theme';
import { Presionable } from '../Presionable';
import { Texto } from '../Texto';
import { COLORES_CAMARA } from './colores';

export type ModoCaptura = 'foto' | 'video';

type Props = {
  modo: ModoCaptura;
  onCambiar: (modo: ModoCaptura) => void;
};

const OPCIONES: { valor: ModoCaptura; texto: string }[] = [
  { valor: 'foto', texto: 'Foto' },
  { valor: 'video', texto: 'Video' },
];


export function SelectorModo({ modo, onCambiar }: Props) {
  return (
    <View style={estilos.contenedor} accessibilityRole="tablist">
      {OPCIONES.map((opcion) => {
        const activo = opcion.valor === modo;
        return (
          <Presionable
            key={opcion.valor}
            onPress={() => onCambiar(opcion.valor)}
            haptico
            accessibilityRole="tab"
            accessibilityLabel={opcion.texto}
            estilo={[estilos.opcion, activo && estilos.opcionActiva]}
          >
            <Texto variante="cuerpoFuerte" color={activo ? COLORES_CAMARA.fondo : COLORES_CAMARA.blanco}>
              {opcion.texto}
            </Texto>
          </Presionable>
        );
      })}
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: {
    flexDirection: 'row',
    padding: espacio.xs,
    borderRadius: radio.pildora,
    backgroundColor: COLORES_CAMARA.vidrio,
  },
  opcion: {
    minWidth: 84,
    minHeight: 40,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: espacio.md,
    borderRadius: radio.pildora,
  },
  opcionActiva: { backgroundColor: COLORES_CAMARA.blanco },
});