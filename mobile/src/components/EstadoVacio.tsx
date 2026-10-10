import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import type { NombreIcono } from '../constants/danos';
import { espacio, useTema } from '../theme';
import { Boton } from './Boton';
import { Texto } from './Texto';

type Props = {
  icono: NombreIcono;
  titulo: string;
  descripcion: string;
  accion?: { texto: string; onPress: () => void };
};


export function EstadoVacio({ icono, titulo, descripcion, accion }: Props) {
  const { paleta } = useTema();
  return (
    <View style={estilos.contenedor}>
      <View style={[estilos.circulo, { backgroundColor: paleta.primarioSuave }]}>
        <Ionicons name={icono} size={34} color={paleta.primario} />
      </View>
      <Texto variante="subtitulo" style={estilos.centrado}>
        {titulo}
      </Texto>
      <Texto suave style={estilos.centrado}>
        {descripcion}
      </Texto>
      {accion ? <Boton texto={accion.texto} onPress={accion.onPress} /> : null}
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { alignItems: 'center', gap: espacio.md, paddingVertical: espacio.xl, paddingHorizontal: espacio.md },
  circulo: { width: 80, height: 80, borderRadius: 40, alignItems: 'center', justifyContent: 'center' },
  centrado: { textAlign: 'center' },
});
