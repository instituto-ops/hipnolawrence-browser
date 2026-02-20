import asyncio
import math
import random

class HumanMouse:
    """
    Simula movimentos humanos de mouse utilizando curvas de Bézier e tempos de reação estocásticos.
    """

    async def move_to_coordinates(self, page, start_x, start_y, target_x, target_y):
        """
        Move o mouse do ponto atual (start_x, start_y) para o alvo (target_x, target_y)
        com comportamento humano simulado.
        """
        
        # Distância Euclidiana para determinar a quantidade de passos
        distance = math.hypot(target_x - start_x, target_y - start_y)
        
        # Define passos dinamicamente (mínimo 15, máximo 50, proporcional à distância)
        steps = int(min(50, max(15, distance / 10)))
        
        # Adiciona um overshoot aleatório (passar um pouco do alvo)
        # O overshoot acontece em cerca de 30% dos movimentos para realismo
        overshoot_x = 0
        overshoot_y = 0
        if random.random() < 0.3:
            overshoot_amount = random.uniform(2, 10)
            angle = math.atan2(target_y - start_y, target_x - start_x)
            overshoot_x = math.cos(angle) * overshoot_amount
            overshoot_y = math.sin(angle) * overshoot_amount

        target_x_adj = target_x + overshoot_x
        target_y_adj = target_y + overshoot_y

        # Define pontos de controle para a Curva de Bézier Cúbica
        # P0 = (start_x, start_y)
        # P3 = (target_x_adj, target_y_adj)
        # P1 e P2 são pontos de controle aleatórios para criar o arco
        
        control_1_x = start_x + (target_x_adj - start_x) * random.uniform(0.2, 0.5) + random.uniform(-50, 50)
        control_1_y = start_y + (target_y_adj - start_y) * random.uniform(0.2, 0.5) + random.uniform(-50, 50)
        
        control_2_x = start_x + (target_x_adj - start_x) * random.uniform(0.5, 0.8) + random.uniform(-50, 50)
        control_2_y = start_y + (target_y_adj - start_y) * random.uniform(0.5, 0.8) + random.uniform(-50, 50)

        path = []
        for i in range(steps + 1):
            t = i / steps
            
            # Equação de Bézier Cúbica
            # B(t) = (1-t)^3 * P0 + 3(1-t)^2 * t * P1 + 3(1-t) * t^2 * P2 + t^3 * P3
            
            x = (math.pow(1 - t, 3) * start_x +
                 3 * math.pow(1 - t, 2) * t * control_1_x +
                 3 * (1 - t) * math.pow(t, 2) * control_2_x +
                 math.pow(t, 3) * target_x_adj)
                 
            y = (math.pow(1 - t, 3) * start_y +
                 3 * math.pow(1 - t, 2) * t * control_1_y +
                 3 * (1 - t) * math.pow(t, 2) * control_2_y +
                 math.pow(t, 3) * target_y_adj)
            
            path.append((x, y))

        # Se houve overshoot, adicionar pequenos passos de correção para voltar ao alvo exato
        if overshoot_x != 0 or overshoot_y != 0:
            correction_steps = 5
            for i in range(1, correction_steps + 1):
                t = i / correction_steps
                # Interpolação linear simples para correção fina
                cx = target_x_adj + (target_x - target_x_adj) * t
                cy = target_y_adj + (target_y - target_y_adj) * t
                path.append((cx, cy))

        # Executar movimento
        for point in path:
            x, y = point
            # Move o mouse na página (playwright page object)
            await page.mouse.move(x, y)
            
            # Delay estocástico entre cada passo do movimento
            # Variação maior no início e fim do movimento (aceleração/desaceleração simulada)
            base_delay = random.uniform(0.005, 0.015) 
            # Ocasionalmente adiciona um "micro-engasgo" humano
            if random.random() < 0.05:
                base_delay += random.uniform(0.01, 0.03)
                
            await asyncio.sleep(base_delay)
            
        # Garante que o mouse termine exatamente no alvo final
        await page.mouse.move(target_x, target_y)
