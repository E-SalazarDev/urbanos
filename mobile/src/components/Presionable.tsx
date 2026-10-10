import * as Haptics from 'expo-haptics';
import { useRef, type ReactNode } from 'react';
import {
  Animated,
  Pressable,
  type AccessibilityRole,
  type GestureResponderEvent,
  type StyleProp,
  type ViewStyle,
} from 'react-native';

type Props = {
  onPress?: (e: GestureResponderEvent) => void;
  disabled?: boolean;
  haptico?: boolean; 
  estilo?: StyleProp<ViewStyle>; 
  estiloContenedor?: StyleProp<ViewStyle>;
  accessibilityLabel?: string;
  accessibilityRole?: AccessibilityRole;
  children: ReactNode;
};


export function Presionable({
  onPress,
  disabled,
  haptico = false,
  estilo,
  estiloContenedor,
  accessibilityLabel,
  accessibilityRole = 'button',
  children,
}: Props) {
  const escala = useRef(new Animated.Value(1)).current;

  const animar = (valor: number) =>
    Animated.spring(escala, { toValue: valor, useNativeDriver: true, speed: 40, bounciness: 6 }).start();

  return (
    <Pressable
      onPressIn={() => animar(0.97)}
      onPressOut={() => animar(1)}
      onPress={(e) => {
        if (haptico) void Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        onPress?.(e);
      }}
      disabled={disabled}
      accessibilityRole={accessibilityRole}
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ disabled: !!disabled }}
      style={estiloContenedor}
    >
      <Animated.View style={[{ transform: [{ scale: escala }] }, estilo]}>{children}</Animated.View>
    </Pressable>
  );
}
