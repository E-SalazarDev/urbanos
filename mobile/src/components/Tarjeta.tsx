import type { ReactNode } from 'react';
import { StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';

import { espacio, radio, sombra, useTema } from '../theme';
import { Presionable } from './Presionable';

type Props = {
  children: ReactNode;
  onPress?: () => void; 
  style?: StyleProp<ViewStyle>;
};

export function Tarjeta({ children, onPress, style }: Props) {
  const { paleta, oscuro } = useTema();
  const estilo = [
    estilos.base,
    { backgroundColor: paleta.superficie, borderColor: paleta.borde },
    oscuro ? null : sombra(1),
    style,
  ];

  if (onPress) {
    return (
      <Presionable onPress={onPress} haptico estilo={estilo}>
        {children}
      </Presionable>
    );
  }
  return <View style={estilo}>{children}</View>;
}

const estilos = StyleSheet.create({
  base: {
    borderRadius: radio.lg,
    borderWidth: StyleSheet.hairlineWidth,
    padding: espacio.md,
    gap: espacio.sm,
  },
});
