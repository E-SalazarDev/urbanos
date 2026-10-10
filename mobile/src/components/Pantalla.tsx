import type { ReactNode } from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { espacio, useTema } from '../theme';
import { Texto } from './Texto';

type Props = {
  titulo: string;
  subtitulo?: string;
  scroll?: boolean; 
  children: ReactNode;
};


export function Pantalla({ titulo, subtitulo, scroll = true, children }: Props) {
  const { paleta } = useTema();
  const insets = useSafeAreaInsets();
  const arriba = insets.top + espacio.md;

  const encabezado = (
    <View style={estilos.encabezado}>
      <Texto variante="titulo" accessibilityRole="header">
        {titulo}
      </Texto>
      {subtitulo ? <Texto suave>{subtitulo}</Texto> : null}
    </View>
  );

  if (!scroll) {
    return (
      <View style={[estilos.contenido, { flex: 1, backgroundColor: paleta.fondo, paddingTop: arriba }]}>
        {encabezado}
        {children}
      </View>
    );
  }

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: paleta.fondo }}
      contentContainerStyle={[estilos.contenido, { paddingTop: arriba }]}
      showsVerticalScrollIndicator={false}
    >
      {encabezado}
      {children}
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  contenido: { paddingHorizontal: espacio.md, paddingBottom: espacio.xl, gap: espacio.md },
  encabezado: { gap: espacio.xs },
});
