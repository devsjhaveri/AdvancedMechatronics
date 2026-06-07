import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0, 360, 1000)

n_detents = 6

force = -np.sin(np.radians(n_detents * theta))

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(theta, force, 'b-', linewidth=2)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
plt.xlabel('Position (degrees)')
plt.ylabel('Force (normalized ±1)')
plt.title(f'Detent Effect - {n_detents} clicks per revolution')
plt.grid(True)
plt.ylim(-1.2, 1.2)

bump_center = 180
bump_width = 30
bump = np.exp(-((theta - bump_center)**2) / (2 * bump_width**2))

plt.subplot(1, 2, 2)
plt.plot(theta, bump, 'r-', linewidth=2)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
plt.xlabel('Position (degrees)')
plt.ylabel('Force (normalized ±1)')
plt.title('Bump Effect - resistance at center')
plt.grid(True)
plt.ylim(-0.2, 1.2)

plt.tight_layout()
plt.savefig('HW18_haptic_effects.png', dpi=150)
plt.show()

print("Detent equation: F = -sin(n * theta)")
print(f"where n = {n_detents} detents per revolution")
print("Bump equation: F = exp(-(theta - center)^2 / (2 * width^2))")